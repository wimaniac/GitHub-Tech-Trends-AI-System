"""
Trend Analyzer — Phân tích xu hướng công nghệ theo thời gian.
Tính toán growth rate, trend score và phát hiện breakout.
"""
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Optional

from analyzer.text_processor import extract_technologies, get_category, prepare_text_for_embedding, discover_new_technologies
from analyzer.embeddings import get_embedding_generator
from analyzer.clustering import cluster_repositories, label_clusters, cluster_technologies, label_technology_clusters
from database.db import (
    get_all_repositories, upsert_trend, add_snapshot,
    get_trends, get_trend_by_name
)


async def analyze_trends():
    """
    Pipeline phân tích xu hướng chính:
    1. Lấy tất cả repos từ DB
    2. Trích xuất công nghệ
    3. Tạo embeddings + clustering
    4. Tính toán trend scores
    5. Lưu kết quả vào DB
    """
    print("\n[Analyzer] === Bắt đầu phân tích xu hướng ===")

    # 1. Lấy repos
    repos = await get_all_repositories()
    if not repos:
        print("[Analyzer] Không có repos để phân tích.")
        return

    print(f"[Analyzer] Phân tích {len(repos)} repositories...")

    # 2. Trích xuất công nghệ cho mỗi repo
    tech_counter: Counter = Counter()       # đếm tổng mentions
    tech_repos: dict[str, list] = defaultdict(list)  # tech -> list repos
    tech_stars: dict[str, list] = defaultdict(list)
    repo_techs: dict[int, list] = {}                # repo index -> techs
    
    unknown_topics: set[str] = set()         # Để discovery công nghệ mới

    for i, repo in enumerate(repos):
        text = f"{repo.description} {repo.readme_content}"
        topics = repo.topics if repo.topics else []
        techs = extract_technologies(text, topics)

        # Thêm ngôn ngữ chính
        if repo.language:
            lang_lower = repo.language.lower()
            if lang_lower not in [t.lower() for t in techs]:
                techs.append(lang_lower)
                
        # Thu thập các topics lạ để tìm kiếm công nghệ mới
        for topic in topics:
            t_lower = topic.lower().strip()
            if t_lower and t_lower not in [t.lower() for t in techs]:
                # Chỉ lấy topic alphabetic hoặc có dấu '-', tránh data rác/ID
                import re
                if re.match(r"^[a-z0-9\-]{2,30}$", t_lower):
                    unknown_topics.add(t_lower)

        repo_techs[i] = techs
        for tech in techs:
            tech_counter[tech] += 1
            tech_repos[tech].append(repo)
            tech_stars[tech].append(repo.stars)
            
    # Init Embedding Generator cho Discovery và Clustering
    emb_gen = None
    try:
        if len(repos) > 0:
            emb_gen = get_embedding_generator()
    except Exception as e:
        print(f"[Analyzer] Lỗi khởi tạo Embedding Model: {e}")

    # 2.5 Dynamic Discovery (Cosine Similarity)
    if emb_gen and unknown_topics:
        discovered_map = discover_new_technologies(list(unknown_topics), emb_gen)
        if discovered_map:
            print(f"[Analyzer] Bổ sung thêm {len(discovered_map)} công nghệ mới vào pipeline.")
            # Map ngược lại vào các repo chứa topic này
            for i, repo in enumerate(repos):
                topics = repo.topics if repo.topics else []
                for topic in topics:
                    t_lower = topic.lower().strip()
                    if t_lower in discovered_map and t_lower not in repo_techs[i]:
                        repo_techs[i].append(t_lower)
                        tech_counter[t_lower] += 1
                        tech_repos[t_lower].append(repo)
                        tech_stars[t_lower].append(repo.stars)

    print(f"[Analyzer] Tìm thấy tổng cộng {len(tech_counter)} công nghệ unique")

    # 3. Embeddings + Clustering Technologies (hệ sinh thái)
    cluster_info: dict = {}
    tech_to_cluster: dict = {}
    if len(repos) >= 5 and emb_gen:
        try:
            texts = [prepare_text_for_embedding(r.__dict__) for r in repos]
            embeddings = emb_gen.generate_batch(texts)
            
            tech_embeddings = {}
            for tech, related_repos in tech_repos.items():
                if len(related_repos) >= 2: # Yêu cầu có ít nhất 2 repo mới nhúng để tránh nhiễu
                    valid_embs = []
                    for r in related_repos:
                        try:
                            idx = repos.index(r)
                            if embeddings[idx] is not None:
                                valid_embs.append(embeddings[idx])
                        except ValueError:
                            pass
                    if valid_embs:
                        tech_embeddings[tech] = np.mean(valid_embs, axis=0).tolist()
                        
            if tech_embeddings:
                result = cluster_technologies(tech_embeddings)
                if result.get("clusters"):
                    cluster_info = label_technology_clusters(result["clusters"], tech_counter)
                    for cid, techs_in_cl in result["clusters"].items():
                        for t in techs_in_cl:
                            tech_to_cluster[t] = cid
                    print(f"[Analyzer] {len(cluster_info)} Tech Ecosystems được phát hiện")
        except Exception as e:
            print(f"[Analyzer] Lỗi clustering technologies: {e}")

    # 4. Tính trend scores và lưu
    trends_saved = 0
    for tech, count in tech_counter.most_common(100):
        related_repos = tech_repos[tech]
        stars_list = tech_stars[tech]

        # Tính metrics
        avg_stars = np.mean(stars_list) if stars_list else 0
        total_stars = sum(stars_list)
        repo_count = len(related_repos)

        # Growth rate: dựa trên repos mới (tạo trong 30 ngày gần đây)
        recent_threshold = datetime.utcnow() - timedelta(days=30)
        recent_repos = [
            r for r in related_repos
            if r.created_at and r.created_at > recent_threshold
        ]
        recent_ratio = len(recent_repos) / max(repo_count, 1)

        # Trend score = tổng hợp nhiều yếu tố
        trend_score = _calculate_trend_score(
            mention_count=count,
            repo_count=repo_count,
            avg_stars=avg_stars,
            recent_ratio=recent_ratio,
            total_stars=total_stars,
        )

        # Growth rate
        growth_rate = recent_ratio * 100

        # Status
        status = _determine_status(growth_rate, trend_score, repo_count)

        # Cấp cluster_id nếu thuộc group
        cl_id = tech_to_cluster.get(tech)

        # Lưu trend
        category = get_category(tech)
        trend_data = {
            "technology_name": tech,
            "category": category,
            "description": f"Detected in {repo_count} repos with avg {avg_stars:.0f} stars",
            "mention_count": count,
            "repo_count": repo_count,
            "avg_stars": avg_stars,
            "growth_rate": growth_rate,
            "trend_score": trend_score,
            "cluster_id": cl_id,
            "status": status,
        }

        trend = await upsert_trend(trend_data)
        if trend:
            # Thêm snapshot
            await add_snapshot(
                trend_id=trend.id,
                score=trend_score,
                repo_count=repo_count,
                mention_count=count,
                avg_stars=avg_stars,
            )
            trends_saved += 1

    print(f"[Analyzer] Đã lưu {trends_saved} xu hướng công nghệ")
    print("[Analyzer] === Phân tích hoàn tất ===\n")
    return trends_saved


def _calculate_trend_score(
    mention_count: int,
    repo_count: int,
    avg_stars: float,
    recent_ratio: float,
    total_stars: int,
) -> float:
    """
    Tính điểm xu hướng tổng hợp (0-100) theo 4 chiều phân tích:
    1. Velocity (35%): Tỷ lệ repo mới (đà tăng trưởng/momentum).
    2. Traction (35%): Sức hút đo bằng tổng log stars.
    3. Frequency (15%): Số lần được nhắc đến trong mô tả/README.
    4. Breadth (15%): Độ phủ (số lượng repo sử dụng độc lập).
    """
    import math
    
    # 1. Velocity (Đà tăng trưởng của công nghệ)
    # Nếu recent_ratio đạt ~66% (2/3 repo là mới) -> đạt điểm tối đa
    velocity_score = min(recent_ratio * 1.5, 1.0) * 35.0
    
    # 2. Traction (Độ viral/hút stars) -> dùng base 10 hoặc tự nhiên
    # Giả định ~160,000 sao (ln ~ 12) là tiệm cận đỉnh cho 1 trend
    traction_score = min(math.log1p(total_stars) / 12.0, 1.0) * 35.0
    
    # 3. Frequency (Mật độ xuất hiện)
    freq_score = min(mention_count / 40.0, 1.0) * 15.0
    
    # 4. Breadth (Độ phủ dự án)
    breadth_score = min(repo_count / 20.0, 1.0) * 15.0
    
    final_score = float(velocity_score + traction_score + freq_score + breadth_score)
    return round(final_score, 2)


def _determine_status(growth_rate: float, trend_score: float, repo_count: int) -> str:
    """Xác định trạng thái xu hướng."""
    if growth_rate > 50 and trend_score > 20:
        return "rising"      # Đang tăng mạnh
    elif growth_rate > 30:
        return "emerging"    # Mới nổi
    elif trend_score > 40:
        return "stable"      # Ổn định, phổ biến
    elif repo_count < 3:
        return "emerging"    # Ít data => coi là mới
    else:
        return "stable"

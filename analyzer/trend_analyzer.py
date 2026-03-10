"""
Trend Analyzer — Phân tích xu hướng công nghệ theo thời gian.
Tính toán growth rate, trend score và phát hiện breakout.
"""
import numpy as np
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Optional

from analyzer.text_processor import extract_technologies, get_category, prepare_text_for_embedding
from analyzer.embeddings import get_embedding_generator
from analyzer.clustering import cluster_repositories, label_clusters
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
    tech_counter = Counter()       # đếm tổng mentions
    tech_repos = defaultdict(list)  # tech -> list repos
    tech_stars = defaultdict(list)
    repo_techs = {}                # repo index -> techs

    for i, repo in enumerate(repos):
        text = f"{repo.description} {repo.readme_content}"
        topics = repo.topics if repo.topics else []
        techs = extract_technologies(text, topics)

        # Thêm ngôn ngữ chính
        if repo.language:
            lang_lower = repo.language.lower()
            if lang_lower not in [t.lower() for t in techs]:
                techs.append(lang_lower)

        repo_techs[i] = techs
        for tech in techs:
            tech_counter[tech] += 1
            tech_repos[tech].append(repo)
            tech_stars[tech].append(repo.stars)

    print(f"[Analyzer] Tìm thấy {len(tech_counter)} công nghệ unique")

    # 3. Embeddings + Clustering (nếu đủ dữ liệu)
    cluster_info = {}
    if len(repos) >= 5:
        try:
            emb_gen = get_embedding_generator()
            texts = [prepare_text_for_embedding(r.__dict__) for r in repos]
            embeddings = emb_gen.generate_batch(texts)

            result = cluster_repositories(embeddings)
            if result.get("clusters"):
                cluster_info = label_clusters(result["clusters"], repo_techs)
                print(f"[Analyzer] {len(cluster_info)} clusters được phát hiện")
        except Exception as e:
            print(f"[Analyzer] Lỗi clustering: {e}")

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

        # Tìm cluster_id
        cl_id = None
        for cid, info in cluster_info.items():
            if any(t["name"] == tech for t in info.get("top_techs", [])):
                cl_id = cid
                break

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
    Tính điểm xu hướng tổng hợp (0-100).
    
    Công thức:
    - 30% từ popularity (log of total stars)
    - 25% từ mention frequency
    - 25% từ recent activity ratio
    - 20% từ repo count
    """
    # Normalize các metrics
    pop_score = min(np.log1p(total_stars) / 15.0, 1.0) * 30
    mention_score = min(mention_count / 50.0, 1.0) * 25
    recent_score = recent_ratio * 25
    repo_score = min(repo_count / 30.0, 1.0) * 20

    return round(pop_score + mention_score + recent_score + repo_score, 2)


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

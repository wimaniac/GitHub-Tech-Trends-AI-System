import asyncio
import random
from datetime import datetime
from typing import Optional

from collector.github_client import GitHubClient
from collector.trending_scraper import TrendingScraper
from database.db import upsert_repositories, get_repo_count, get_all_repo_names
from analyzer.text_processor import CATEGORY_MAP


async def collect_trending():
    """Thu thập repos từ GitHub Trending."""
    print(f"\n[Collector] === Bắt đầu thu thập trending ({datetime.utcnow().isoformat()}) ===")

    scraper = TrendingScraper()
    try:
        repos = await scraper.scrape_all_trending()
        if repos:
            # Lọc repo đã có
            existing_repos = await get_all_repo_names()
            new_repos = [r for r in repos if r.get("full_name") not in existing_repos]
            print(f"[Collector] Scrape Trending ra {len(repos)} repos, trong đó {len(new_repos)} là mới.")
            
            if new_repos:
                count = await upsert_repositories(new_repos)
                print(f"[Collector] Đã lưu thêm {count} trending repos mới.")
            else:
                print(f"[Collector] Các trending repos đều đã tồn tại trong DB.")
        else:
            print("[Collector] Không tìm thấy trending repos nào.")
    except Exception as e:
        print(f"[Collector] Lỗi scrape trending: {e}")
    finally:
        await scraper.close()


async def collect_search(queries: Optional[list[str]] = None):
    """Thu thập repos MỚI NỔI đa dạng theo chủ đề và lọc trùng lặp."""
    print(f"\n[Collector] === Bắt đầu search emerging repos ({datetime.utcnow().isoformat()}) ===")

    if queries is None:
        from datetime import timedelta
        date_90d = (datetime.utcnow() - timedelta(days=90)).strftime("%Y-%m-%d")
        date_30d = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
        date_7d = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Base queries cho repos mới nổi siêu tốc
        queries = [
            f"created:>{date_30d} stars:>50",
            f"created:>{date_7d} stars:>10",
        ]
        
        # Mix chủ đề để không bị bias: Lấy ngẫu nhiên vài danh mục
        categories = list(CATEGORY_MAP.keys())
        random.shuffle(categories)
        
        # Chọn 6 danh mục khác nhau mỗi lần chạy để đảm bảo bao phủ rộng
        for cat in categories[:6]:
            if CATEGORY_MAP[cat]:
                tech = random.choice(list(CATEGORY_MAP[cat]))
                queries.append(f"topic:{tech} created:>{date_90d} stars:>20")

    # Lấy danh sách repo đã có để lọc
    existing_repos = await get_all_repo_names()

    client = GitHubClient()
    total = 0
    try:
        for query_str in queries:
            print(f"[Collector] Searching: {query_str}")
            # Search repos trực tiếp (không lấy README ngay)
            raw_repos = await client.search_repositories(query=query_str, per_page=30)
            
            # Lọc trùng lặp
            new_repos = []
            for r in raw_repos:
                if r.get("full_name") not in existing_repos:
                    new_repos.append(r)
            
            print(f"  -> Trả về {len(raw_repos)} repos, trong đó có {len(new_repos)} repo hoàn toàn mới.")

            if new_repos:
                # Chỉ Get README cho repo mới
                for repo in new_repos:
                    parts = repo.get("full_name", "").split("/")
                    if len(parts) == 2:
                        readme = await client.get_readme(parts[0], parts[1])
                        repo["readme_content"] = readme
                
                # Cập nhật DB
                count = await upsert_repositories(new_repos)
                total += int(count)
                
                # Thêm vào tập hiện tại để tránh duplicate ở các query sau cùng phiên
                for r in new_repos:
                    if r.get("full_name"):
                        existing_repos.add(r["full_name"])
                        
            await asyncio.sleep(2)
    except Exception as e:
        print(f"[Collector] Lỗi search: {e}")
    finally:
        await client.close()

    print(f"[Collector] Tổng cộng đã thu thập thêm: {total} repos mới")
    total_db = await get_repo_count()
    print(f"[Collector] Tổng repos trong DB: {total_db}")
    return total


async def collect_all():
    """Thu thập toàn bộ: trending + search."""
    await collect_trending()
    await collect_search()

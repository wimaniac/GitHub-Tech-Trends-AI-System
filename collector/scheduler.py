"""
Scheduler — Lập lịch thu thập dữ liệu định kỳ.
"""
import asyncio
from datetime import datetime

from collector.github_client import GitHubClient
from collector.trending_scraper import TrendingScraper
from database.db import upsert_repositories, get_repo_count


async def collect_trending():
    """Thu thập repos từ GitHub Trending."""
    print(f"\n[Collector] === Bắt đầu thu thập trending ({datetime.utcnow().isoformat()}) ===")

    scraper = TrendingScraper()
    try:
        repos = await scraper.scrape_all_trending()
        if repos:
            count = await upsert_repositories(repos)
            print(f"[Collector] Đã lưu {count} trending repos.")
        else:
            print("[Collector] Không tìm thấy trending repos nào.")
    except Exception as e:
        print(f"[Collector] Lỗi scrape trending: {e}")
    finally:
        await scraper.close()


async def collect_search(queries: list[str] = None):
    """Thu thập repos từ GitHub Search API."""
    print(f"\n[Collector] === Bắt đầu search repos ({datetime.utcnow().isoformat()}) ===")

    if queries is None:
        queries = [
            "stars:>1000 pushed:>2026-02-01",
            "topic:machine-learning stars:>100",
            "topic:artificial-intelligence stars:>100",
            "topic:web-framework stars:>100",
            "topic:deep-learning stars:>50",
            "topic:llm stars:>50",
            "topic:rust stars:>200",
            "topic:devops stars:>100",
        ]

    client = GitHubClient()
    total = 0
    try:
        for query in queries:
            print(f"[Collector] Searching: {query}")
            repos = await client.search_and_get_details(
                query=query,
                max_repos=30,
                include_readme=True
            )
            if repos:
                count = await upsert_repositories(repos)
                total += count
                print(f"[Collector] Tìm thấy {count} repos cho query: {query[:50]}...")
            await asyncio.sleep(2)
    except Exception as e:
        print(f"[Collector] Lỗi search: {e}")
    finally:
        await client.close()

    print(f"[Collector] Tổng cộng đã thu thập: {total} repos")
    total_db = await get_repo_count()
    print(f"[Collector] Tổng repos trong DB: {total_db}")
    return total


async def collect_all():
    """Thu thập toàn bộ: trending + search."""
    await collect_trending()
    await collect_search()

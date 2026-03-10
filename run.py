"""
Entry point cho GitHub Tech Trends AI System.
Có tích hợp APScheduler để tự động crawl dữ liệu định kỳ.
"""
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import API_HOST, API_PORT, COLLECT_INTERVAL_HOURS, ANALYSIS_INTERVAL_HOURS
from collector.scheduler import collect_all
from analyzer.trend_analyzer import analyze_trends

# Global scheduler instance
scheduler = AsyncIOScheduler()

async def scheduled_collect_task():
    """Task tự động thu thập và phân tích định kỳ."""
    try:
        print("[Scheduler] Bắt đầu job tự động thu thập...")
        await collect_all()
        print("[Scheduler] Bắt đầu phân tích AI...")
        await analyze_trends()
        print("[Scheduler] Hoàn tất job định kỳ.")
    except Exception as e:
        print(f"[Scheduler] Lỗi trong job định kỳ: {e}")

def setup_scheduler():
    """Cấu hình các jobs cho scheduler."""
    # Job thu thập dữ liệu (mặc định mỗi 6h)
    scheduler.add_job(
        scheduled_collect_task,
        trigger=IntervalTrigger(hours=COLLECT_INTERVAL_HOURS),
        id="auto_collection_job",
        name="Thu thập dữ liệu GitHub tự động",
        replace_existing=True,
    )
    print(f"[Scheduler] Đã cấu hình auto-collect mỗi {COLLECT_INTERVAL_HOURS} giờ.")

def main():
    print("=" * 60)
    print("  🔍 GitHub Tech Trends AI System")
    print("  📊 Phân tích xu hướng công nghệ từ GitHub")
    print("=" * 60)
    print(f"\n  Dashboard: http://localhost:{API_PORT}")
    print(f"  API Docs:  http://localhost:{API_PORT}/docs")
    print(f"\n  Các bước sử dụng:")
    print(f"  1. Mở dashboard tại URL trên")
    print(f"  2. Nhấn 'Thu thập dữ liệu' để crawl GitHub")
    print(f"  3. Chờ phân tích AI hoàn tất")
    print(f"  4. Xem xu hướng công nghệ trên dashboard")
    print(f"  (Hệ thống tự động crawl mỗi {COLLECT_INTERVAL_HOURS} giờ)")
    print("=" * 60)

    # Chạy Uvicorn trực tiếp
    # Lưu ý: Việc start scheduler sẽ được đưa vào lifespan của app FastAPI
    uvicorn.run(
        "api.app:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info",
    )

if __name__ == "__main__":
    main()

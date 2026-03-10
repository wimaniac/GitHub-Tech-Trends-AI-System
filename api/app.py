"""
FastAPI Application — API server cho GitHub Tech Trends.
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from config import BASE_DIR
from database.db import init_db
from api.routes import router

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
# Import scheduler từ run.py (sẽ được tách biệt logic một cách an toàn)
import sys
# Để import đúng run.py, chúng ta cần tránh circular import bằng cách start trực tiếp trong app
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import COLLECT_INTERVAL_HOURS
from collector.scheduler import collect_all
from analyzer.trend_analyzer import analyze_trends

scheduler = AsyncIOScheduler()

async def scheduled_collect_task():
    try:
        print("[Scheduler] Bắt đầu job tự động thu thập...")
        await collect_all()
        print("[Scheduler] Bắt đầu phân tích AI...")
        await analyze_trends()
        print("[Scheduler] Hoàn tất job định kỳ.")
    except Exception as e:
        print(f"[Scheduler] Lỗi trong job định kỳ: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup và shutdown events."""
    # Startup
    print("[Server] Khởi tạo database...")
    await init_db()
    
    print("[Server] Khởi tạo API Cache...")
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

    print(f"[Server] Khởi động Background Scheduler (Chu kỳ: {COLLECT_INTERVAL_HOURS}h)...")
    scheduler.add_job(
        scheduled_collect_task,
        trigger=IntervalTrigger(hours=COLLECT_INTERVAL_HOURS),
        id="auto_collection_job",
        replace_existing=True,
    )
    scheduler.start()
    
    print("[Server] Server đã sẵn sàng! 🚀")
    yield
    # Shutdown
    print("[Server] Đang tắt server...")


app = FastAPI(
    title="GitHub Tech Trends AI",
    description="Hệ thống AI phân tích xu hướng công nghệ từ GitHub",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(router, prefix="/api")

# Serve dashboard static files
dashboard_dir = BASE_DIR / "dashboard"
if dashboard_dir.exists():
    app.mount("/static", StaticFiles(directory=str(dashboard_dir)), name="static")


@app.get("/")
async def serve_dashboard():
    """Serve dashboard HTML."""
    index_path = dashboard_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "GitHub Tech Trends AI API", "docs": "/docs"}

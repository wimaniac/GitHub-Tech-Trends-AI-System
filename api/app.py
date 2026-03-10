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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup và shutdown events."""
    # Startup
    print("[Server] Khởi tạo database...")
    await init_db()
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

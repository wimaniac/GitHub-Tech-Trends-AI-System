"""
API Routes — Endpoints cho GitHub Tech Trends.
"""
import asyncio
from fastapi import APIRouter, Query, BackgroundTasks
from typing import Optional
from fastapi_cache.decorator import cache

from database.db import (
    get_trends, get_trend_by_name, get_trend_timeline,
    get_categories, get_repositories, get_repo_count
)
from analyzer.trend_analyzer import analyze_trends
from analyzer.predictor import predict_trends
from collector.scheduler import collect_all, collect_trending, collect_search

router = APIRouter()


@router.get("/trends")
@cache(expire=1800)  # Cache 30 phút
async def api_get_trends(
    limit: int = Query(30, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("trend_score", pattern="^(trend_score|growth_rate|stars|repo_count|mention_count)$"),
):
    """Lấy danh sách xu hướng công nghệ."""
    # Map sort field
    sort_map = {
        "trend_score": "trend_score",
        "growth_rate": "growth_rate",
        "stars": "avg_stars",
        "repo_count": "repo_count",
        "mention_count": "mention_count",
    }
    sort_field = sort_map.get(sort_by, "trend_score")

    trends = await get_trends(
        limit=limit,
        category=category,
        status=status,
        sort_by=sort_field
    )
    return {
        "count": len(trends),
        "trends": [t.to_dict() for t in trends],
    }


@router.get("/trends/detail/{tech_name}")
@cache(expire=1800)
async def api_get_trend_detail(tech_name: str):
    """Lấy chi tiết 1 xu hướng công nghệ."""
    trend = await get_trend_by_name(tech_name)
    if not trend:
        return {"error": f"Không tìm thấy: {tech_name}"}

    # Lấy timeline
    timeline = await get_trend_timeline(tech_name=tech_name)

    return {
        "trend": trend.to_dict(),
        "timeline": timeline,
    }


@router.get("/trends/timeline")
@cache(expire=1800)
async def api_get_timeline(
    tech_name: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
):
    """Lấy dữ liệu timeline cho charts."""
    timeline = await get_trend_timeline(tech_name=tech_name, days=days)
    return {
        "count": len(timeline),
        "timeline": timeline,
    }


@router.get("/categories")
@cache(expire=3600)  # Cache 1 giờ
async def api_get_categories():
    """Lấy danh sách categories."""
    categories = await get_categories()
    return {"categories": categories}


@router.get("/predictions")
@cache(expire=3600)
async def api_get_predictions(top_n: int = Query(15, ge=1, le=50)):
    """Lấy dự đoán xu hướng."""
    predictions = await predict_trends(top_n=top_n)
    return {
        "count": len(predictions),
        "predictions": predictions,
    }


@router.get("/repos")
@cache(expire=900)  # Cache 15 phút
async def api_get_repos(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    language: Optional[str] = None,
):
    """Lấy danh sách repositories đã thu thập."""
    repos = await get_repositories(limit=limit, offset=offset, language=language)
    return {
        "count": len(repos),
        "repos": [r.to_dict() for r in repos],
    }


@router.get("/stats")
@cache(expire=900)
async def api_get_stats():
    """Thống kê tổng quan."""
    repo_count = await get_repo_count()
    trends = await get_trends(limit=1000)
    categories = await get_categories()

    rising_count = sum(1 for t in trends if t.status == "rising")
    emerging_count = sum(1 for t in trends if t.status == "emerging")

    return {
        "total_repos": repo_count,
        "total_trends": len(trends),
        "rising_count": rising_count,
        "emerging_count": emerging_count,
        "categories": len(categories),
    }


@router.post("/collect")
async def api_trigger_collect(background_tasks: BackgroundTasks, query: Optional[str] = None):
    """Kích hoạt thu thập dữ liệu thủ công."""
    background_tasks.add_task(_run_collection, query)
    msg_suffix = f" cho từ khóa '{query}'" if query else ""
    return {
        "status": "started",
        "message": f"Đang thu thập dữ liệu{msg_suffix}... Kiểm tra console để xem tiến trình."
    }


@router.post("/analyze")
async def api_trigger_analyze(background_tasks: BackgroundTasks):
    """Kích hoạt phân tích AI thủ công."""
    background_tasks.add_task(_run_analysis)
    return {
        "status": "started",
        "message": "Đang phân tích xu hướng..."
    }


async def _run_collection(query: Optional[str] = None):
    """Background task: thu thập dữ liệu."""
    try:
        if query:
            # Thu thập theo từ khóa người dùng nhập (tìm kiếm repo có star > 10 cho có chất lượng)
            await collect_search([f"{query} stars:>10"])
        else:
            await collect_all()
        await analyze_trends()
    except Exception as e:
        print(f"[API] Lỗi collection: {e}")


async def _run_analysis():
    """Background task: phân tích."""
    try:
        await analyze_trends()
    except Exception as e:
        print(f"[API] Lỗi analysis: {e}")

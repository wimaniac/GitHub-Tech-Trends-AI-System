"""
API Routes — Endpoints cho GitHub Tech Trends.
"""
import asyncio
import json
from fastapi import APIRouter, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Optional
from fastapi_cache.decorator import cache

from database.db import (
    get_trends, get_trend_by_name, get_trend_timeline,
    get_categories, get_repositories, get_repo_count,
    search_suggestions, search_repositories,
)
from analyzer.trend_analyzer import analyze_trends
from analyzer.predictor import predict_trends
from collector.scheduler import collect_all, collect_trending, collect_search
from config import GEMINI_API_KEY, GEMINI_MODEL

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


@router.get("/repos/search")
async def api_search_repos(
    q: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
):
    """Tìm kiếm repositories theo từ khóa."""
    repos = await search_repositories(query=q, limit=limit)
    return {
        "count": len(repos),
        "repos": [r.to_dict() for r in repos],
    }


@router.get("/search/suggestions")
async def api_search_suggestions(
    q: str = Query(..., min_length=2),
):
    """Gợi ý autocomplete cho search box."""
    suggestions = await search_suggestions(query=q)
    return {"suggestions": suggestions}


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


@router.post("/chat")
async def api_chat(body: dict):
    """Gemini AI Chatbot — trả lời câu hỏi về trends, tìm repo, phân tích."""
    message = body.get("message", "").strip()
    if not message:
        return {"response": "Vui lòng nhập câu hỏi.", "suggestions": []}

    if not GEMINI_API_KEY:
        return {
            "response": "⚠️ Chưa cấu hình Gemini API Key. Vui lòng thêm GEMINI_API_KEY vào file .env",
            "suggestions": [],
        }

    try:
        # Lấy context từ DB
        trends = await get_trends(limit=30)
        categories = await get_categories()
        repo_count = await get_repo_count()

        trends_context = "\n".join([
            f"- {t.technology_name} (category: {t.category}, score: {t.trend_score:.1f}, "
            f"growth: {t.growth_rate:.1f}%, repos: {t.repo_count}, status: {t.status})"
            for t in trends[:20]
        ])

        cats_context = ", ".join([f"{c['category']} ({c['count']})" for c in categories])

        # Kiểm tra nếu user muốn tìm repo cụ thể
        search_results_context = ""
        search_keywords = _extract_search_intent(message)
        if search_keywords:
            found_repos = await search_repositories(query=search_keywords, limit=10)
            if found_repos:
                search_results_context = "\n\nKết quả tìm kiếm repos liên quan:\n" + "\n".join([
                    f"- {r.full_name} ⭐{r.stars} ({r.language or 'N/A'}): {(r.description or '')[:100]}"
                    for r in found_repos
                ])

        system_prompt = f"""Bạn là trợ lý AI chuyên về xu hướng công nghệ trên GitHub. Bạn có quyền truy cập dữ liệu sau:

📊 Tổng quan: {repo_count} repositories, {len(trends)} xu hướng công nghệ
📂 Danh mục: {cats_context}

🔥 Top xu hướng hiện tại:
{trends_context}
{search_results_context}

Hướng dẫn:
- Trả lời bằng ngôn ngữ mà user sử dụng (Tiếng Việt hoặc English)
- Sử dụng dữ liệu thực từ hệ thống để trả lời
- Nếu user hỏi về 1 công nghệ cụ thể, cung cấp thông tin chi tiết
- Nếu user muốn tìm repo, liệt kê repos phù hợp từ dữ liệu
- Nếu user muốn phân tích, đưa ra nhận xét chuyên sâu
- Sử dụng emoji để làm câu trả lời sinh động
- Trả lời ngắn gọn, súc tích, dưới 500 từ
- Format markdown nếu cần (headings, lists, bold, etc.)"""

        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                {"role": "user", "parts": [{"text": system_prompt + "\n\nCâu hỏi: " + message}]},
            ],
        )

        ai_response = response.text if response.text else "Xin lỗi, tôi không thể trả lời câu hỏi này."

        # Tạo gợi ý follow-up
        suggestions = _generate_suggestions(message, trends[:5])

        return {
            "response": ai_response,
            "suggestions": suggestions,
        }

    except Exception as e:
        print(f"[Chat] Error: {e}")
        return {
            "response": f"❌ Đã xảy ra lỗi: {str(e)}",
            "suggestions": [],
        }


def _extract_search_intent(message: str) -> str:
    """Trích xuất từ khóa tìm kiếm từ câu hỏi."""
    msg_lower = message.lower()
    keywords = ["tìm", "search", "find", "repo", "repository", "liên quan", "related",
                 "phân tích", "analyze", "về", "about"]
    
    # Nếu có intent tìm kiếm, trả về phần còn lại sau keyword
    for kw in keywords:
        if kw in msg_lower:
            idx = msg_lower.index(kw) + len(kw)
            remaining = message[idx:].strip().strip("?!.,")
            if len(remaining) >= 2:
                return remaining[:50]
    return ""


def _generate_suggestions(message: str, top_trends: list) -> list:
    """Tạo gợi ý follow-up cho chatbot."""
    suggestions = []
    if top_trends:
        suggestions.append(f"So sánh {top_trends[0].technology_name} với {top_trends[1].technology_name}" if len(top_trends) > 1 else "")
        suggestions.append(f"Phân tích chi tiết {top_trends[0].technology_name}")
        suggestions.append("Xu hướng nào đang tăng mạnh nhất?")
    return [s for s in suggestions if s]


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

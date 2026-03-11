"""
Database operations cho GitHub Tech Trends AI System.
Cung cấp các hàm CRUD cho repos, trends và snapshots.
"""
import asyncio
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func, update, delete
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from config import DATABASE_URL
from database.models import Base, Repository, TechTrend, TrendSnapshot

# Engine và session factory
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Tạo bảng nếu chưa có."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] Đã khởi tạo database.")


async def get_session() -> AsyncSession:
    """Lấy session mới."""
    return async_session()


# === Repository CRUD ===

async def upsert_repository(repo_data: dict) -> Optional[Repository]:
    """Thêm hoặc cập nhật repository."""
    async with async_session() as session:
        # Tìm repo đã tồn tại
        result = await session.execute(
            select(Repository).where(Repository.full_name == repo_data.get("full_name"))
        )
        existing = result.scalar_one_or_none()

        if existing:
            # Cập nhật thông tin mới
            for key, value in repo_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.collected_at = datetime.utcnow()
            await session.commit()
            return existing
        else:
            # Tạo mới
            repo = Repository(**repo_data)
            repo.collected_at = datetime.utcnow()
            session.add(repo)
            await session.commit()
            return repo


async def upsert_repositories(repos_data: list[dict]) -> int:
    """Batch upsert nhiều repositories. Trả về số lượng đã xử lý."""
    count = 0
    for repo_data in repos_data:
        try:
            repo = await upsert_repository(repo_data)
            if repo:
                count += 1
        except Exception as e:
            print(f"[DB] Lỗi upsert repo {repo_data.get('full_name', '?')}: {e}")
    return count


async def get_repositories(limit: int = 100, offset: int = 0, language: str | None = None):
    """Lấy danh sách repositories."""
    async with async_session() as session:
        query = select(Repository).order_by(Repository.stars.desc())
        if language:
            query = query.where(Repository.language == language)
        query = query.limit(limit).offset(offset)
        result = await session.execute(query)
        return result.scalars().all()


async def get_all_repositories():
    """Lấy toàn bộ repositories cho phân tích."""
    async with async_session() as session:
        result = await session.execute(
            select(Repository).order_by(Repository.collected_at.desc())
        )
        return result.scalars().all()


async def get_all_repo_names() -> set[str]:
    """Lấy tập hợp full_name của toàn bộ repos để check trùng lặp."""
    async with async_session() as session:
        result = await session.execute(select(Repository.full_name))
        return set(result.scalars().all())


async def get_repo_count():
    """Đếm tổng số repositories."""
    async with async_session() as session:
        result = await session.execute(select(func.count(Repository.id)))
        return result.scalar() or 0


# === TechTrend CRUD ===

async def upsert_trend(trend_data: dict) -> Optional[TechTrend]:
    """Thêm hoặc cập nhật tech trend."""
    async with async_session() as session:
        result = await session.execute(
            select(TechTrend).where(
                TechTrend.technology_name == trend_data.get("technology_name")
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            for key, value in trend_data.items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.last_seen = datetime.utcnow()
            await session.commit()
            return existing
        else:
            trend = TechTrend(**trend_data)
            trend.first_seen = datetime.utcnow()
            trend.last_seen = datetime.utcnow()
            session.add(trend)
            await session.commit()
            return trend


async def get_trends(
    limit: int = 50,
    category: str | None = None,
    status: str | None = None,
    sort_by: str = "trend_score"
):
    """Lấy danh sách xu hướng công nghệ."""
    async with async_session() as session:
        query = select(TechTrend)
        if category:
            query = query.where(TechTrend.category == category)
        if status:
            query = query.where(TechTrend.status == status)

        # Sắp xếp
        sort_col = getattr(TechTrend, sort_by, TechTrend.trend_score)
        query = query.order_by(sort_col.desc()).limit(limit)

        result = await session.execute(query)
        return result.scalars().all()


async def get_trend_by_name(tech_name: str) -> Optional[TechTrend]:
    """Tìm trend theo tên công nghệ."""
    async with async_session() as session:
        result = await session.execute(
            select(TechTrend).where(TechTrend.technology_name == tech_name)
        )
        return result.scalar_one_or_none()


async def get_categories():
    """Lấy danh sách categories và số lượng trends."""
    async with async_session() as session:
        result = await session.execute(
            select(TechTrend.category, func.count(TechTrend.id))
            .group_by(TechTrend.category)
            .order_by(func.count(TechTrend.id).desc())
        )
        return [{"category": row[0], "count": row[1]} for row in result.all()]


# === TrendSnapshot CRUD ===

async def add_snapshot(trend_id: int, score: float, repo_count: int, mention_count: int, avg_stars: float):
    """Thêm snapshot cho trend."""
    async with async_session() as session:
        snapshot = TrendSnapshot(
            trend_id=trend_id,
            date=datetime.utcnow(),
            score=score,
            repo_count=repo_count,
            mention_count=mention_count,
            avg_stars=avg_stars,
        )
        session.add(snapshot)
        await session.commit()
        return snapshot


async def get_trend_timeline(tech_name: str | None = None, days: int = 30):
    """Lấy dữ liệu timeline cho charts."""
    async with async_session() as session:
        query = (
            select(TrendSnapshot, TechTrend.technology_name)
            .join(TechTrend)
            .order_by(TrendSnapshot.date.asc())
        )
        if tech_name:
            query = query.where(TechTrend.technology_name == tech_name)

        result = await session.execute(query)
        rows = result.all()
        return [
            {
                "technology_name": row[1],
                **row[0].to_dict()
            }
            for row in rows
        ]


async def search_suggestions(query: str, limit: int = 8):
    """Tìm gợi ý autocomplete từ trends và repos."""
    if not query or len(query) < 2:
        return []

    async with async_session() as session:
        pattern = f"%{query}%"
        suggestions = []

        # Tìm trong tech_trends
        result = await session.execute(
            select(TechTrend.technology_name, TechTrend.category, TechTrend.trend_score)
            .where(TechTrend.technology_name.ilike(pattern))
            .order_by(TechTrend.trend_score.desc())
            .limit(limit)
        )
        for row in result.all():
            suggestions.append({
                "type": "trend",
                "name": row[0],
                "category": row[1],
                "score": round(row[2], 1),
            })

        # Tìm trong repositories (nếu chưa đủ)
        remaining = limit - len(suggestions)
        if remaining > 0:
            result = await session.execute(
                select(Repository.full_name, Repository.language, Repository.stars)
                .where(
                    (Repository.full_name.ilike(pattern)) |
                    (Repository.description.ilike(pattern))
                )
                .order_by(Repository.stars.desc())
                .limit(remaining)
            )
            for row in result.all():
                suggestions.append({
                    "type": "repo",
                    "name": row[0],
                    "language": row[1],
                    "stars": row[2],
                })

        return suggestions


async def search_repositories(query: str, limit: int = 20):
    """Full-text search trong repositories."""
    if not query:
        return []

    async with async_session() as session:
        pattern = f"%{query}%"
        result = await session.execute(
            select(Repository)
            .where(
                (Repository.full_name.ilike(pattern)) |
                (Repository.description.ilike(pattern)) |
                (Repository.name.ilike(pattern))
            )
            .order_by(Repository.stars.desc())
            .limit(limit)
        )
        return result.scalars().all()


async def clear_all_data():
    """Xóa toàn bộ dữ liệu (dùng cho reset)."""
    async with async_session() as session:
        await session.execute(delete(TrendSnapshot))
        await session.execute(delete(TechTrend))
        await session.execute(delete(Repository))
        await session.commit()
    print("[DB] Đã xóa toàn bộ dữ liệu.")

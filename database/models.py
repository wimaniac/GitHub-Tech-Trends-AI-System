"""
SQLAlchemy models cho GitHub Tech Trends AI System.
Định nghĩa các bảng: Repository, TechTrend, TrendSnapshot.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Repository(Base):
    """Lưu thông tin repository đã thu thập."""
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    github_id = Column(Integer, unique=True, nullable=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(500), unique=True, nullable=False)
    description = Column(Text, default="")
    url = Column(String(500), nullable=False)
    language = Column(String(100), default="")
    stars = Column(Integer, default=0)
    forks = Column(Integer, default=0)
    open_issues = Column(Integer, default=0)
    topics = Column(JSON, default=list)           # danh sách tags/topics
    readme_content = Column(Text, default="")
    created_at = Column(DateTime, nullable=True)   # ngày tạo repo trên GitHub
    collected_at = Column(DateTime, default=datetime.utcnow)  # ngày thu thập
    stars_today = Column(Integer, default=0)        # stars gained today (trending)
    embedding = Column(JSON, nullable=True)         # vector embedding đã cache

    def __repr__(self):
        return f"<Repository(full_name='{self.full_name}', stars={self.stars})>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "description": self.description,
            "url": self.url,
            "language": self.language,
            "stars": self.stars,
            "forks": self.forks,
            "topics": self.topics or [],
            "stars_today": self.stars_today,
            "collected_at": self.collected_at.isoformat() if self.collected_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TechTrend(Base):
    """Lưu xu hướng công nghệ đã phát hiện."""
    __tablename__ = "tech_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    technology_name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100), default="general")  # AI, Web, DevOps, etc.
    description = Column(Text, default="")
    mention_count = Column(Integer, default=0)          # tổng số lần mention
    repo_count = Column(Integer, default=0)             # số repo liên quan
    avg_stars = Column(Float, default=0.0)              # trung bình stars
    growth_rate = Column(Float, default=0.0)            # tốc độ tăng trưởng (%)
    trend_score = Column(Float, default=0.0)            # điểm xu hướng tổng hợp
    cluster_id = Column(Integer, nullable=True)         # cluster ID từ AI
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="rising")       # rising, stable, declining, emerging

    # Quan hệ với snapshots
    snapshots = relationship("TrendSnapshot", back_populates="trend", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<TechTrend(name='{self.technology_name}', score={self.trend_score})>"

    def to_dict(self):
        return {
            "id": self.id,
            "technology_name": self.technology_name,
            "category": self.category,
            "description": self.description,
            "mention_count": self.mention_count,
            "repo_count": self.repo_count,
            "avg_stars": round(self.avg_stars, 1),
            "growth_rate": round(self.growth_rate, 2),
            "trend_score": round(self.trend_score, 2),
            "status": self.status,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class TrendSnapshot(Base):
    """Dữ liệu time-series cho từng xu hướng (mỗi snapshot = 1 ngày)."""
    __tablename__ = "trend_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    trend_id = Column(Integer, ForeignKey("tech_trends.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    score = Column(Float, default=0.0)
    repo_count = Column(Integer, default=0)
    mention_count = Column(Integer, default=0)
    avg_stars = Column(Float, default=0.0)

    trend = relationship("TechTrend", back_populates="snapshots")

    def to_dict(self):
        return {
            "date": self.date.isoformat() if self.date else None,
            "score": round(self.score, 2),
            "repo_count": self.repo_count,
            "mention_count": self.mention_count,
            "avg_stars": round(self.avg_stars, 1),
        }

from sqlalchemy import Column, String, Integer, TIMESTAMP
from sqlalchemy.sql import func
from .database import Base


class ScraperAnalytics(Base):
    __tablename__ = "scraper_analytics"

    source = Column(String, primary_key=True, index=True)
    total_articles = Column(Integer, nullable=False)
    total_images = Column(Integer, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class ScraperAnalyticsHistory(Base):
    __tablename__ = "scraper_analytics_history"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)
    total_articles = Column(Integer)
    total_images = Column(Integer)
    snapshot_time = Column(TIMESTAMP, server_default=func.now())
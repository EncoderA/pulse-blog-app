from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String, SmallInteger
from typing import Optional, List
from datetime import datetime


class TimelinePost(SQLModel, table=True):
    __tablename__ = "timeline_posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: str = Field(max_length=100, unique=True)
    kb_source: Optional[str] = None
    slug: Optional[str] = Field(default=None, max_length=255, unique=True)

    # Section 1: Post
    title: Optional[str] = None
    short_summary: Optional[str] = None

    # Section 2: Post Metadata
    published_at: Optional[datetime] = None
    content_length: Optional[int] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    is_trending: bool = Field(default=False)
    is_ai_policy: bool = Field(default=False)

    # Section 3: QuickTake
    quick_take: Optional[str] = None

    # Section 5: Detailed Summary
    background: Optional[str] = None
    what_happened: Optional[str] = None
    key_highlights: Optional[str] = None  # \n-delimited plain text
    impact: Optional[str] = None
    whats_next: Optional[str] = None

    # Section 8: Key Facts
    policy_announced: bool = Field(default=False)
    focus_area: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    overview: Optional[str] = None
    impacts_detail: Optional[str] = None

    # Section 9: Primary Image
    primary_image_url: Optional[str] = None

    ingest_status: Optional[str] = Field(default="pending", max_length=50)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

    # AI enrichment tracking
    retry_count: int = Field(default=0)
    enriched_at: Optional[datetime] = None
    enrichment_model: Optional[str] = Field(default=None, max_length=100)
    agent_config_id: Optional[int] = None

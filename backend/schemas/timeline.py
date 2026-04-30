from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TimelineEventOut(BaseModel):
    id: int
    event_time: Optional[datetime] = None
    event_title: Optional[str] = None
    event_content: Optional[str] = None
    event_image_url: Optional[str] = None
    sequence_order: int

    class Config:
        from_attributes = True


class TimelineQuoteOut(BaseModel):
    id: int
    quote_text: str
    attributed_to: Optional[str] = None

    class Config:
        from_attributes = True


class TimelineCommentOut(BaseModel):
    id: int
    comment_text: str
    commenter_name: Optional[str] = None
    commenter_designation: Optional[str] = None
    commenter_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class TimelinePostSummary(BaseModel):
    id: int
    slug: Optional[str] = None
    title: Optional[str] = None
    short_summary: Optional[str] = None
    published_at: Optional[datetime] = None
    focus_area: Optional[List[str]] = None
    is_trending: bool = False
    primary_image_url: Optional[str] = None
    ingest_status: Optional[str] = None

    class Config:
        from_attributes = True


class TimelinePostDetail(TimelinePostSummary):
    quick_take: Optional[str] = None
    background: Optional[str] = None
    what_happened: Optional[str] = None
    key_highlights: Optional[str] = None  # \n-delimited plain text
    impact: Optional[str] = None
    whats_next: Optional[str] = None
    overview: Optional[str] = None
    impacts_detail: Optional[str] = None
    source_url: Optional[str] = None
    events: List[TimelineEventOut] = []
    quotes: List[TimelineQuoteOut] = []
    comments: List[TimelineCommentOut] = []

    class Config:
        from_attributes = True

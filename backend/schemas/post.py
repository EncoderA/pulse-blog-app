from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostRead(BaseModel):
    id: str
    title: str
    summary: str
    main_content: str
    img_url: Optional[str]
    article_source_urls: List[str]
    focus_areas: List[str]
    published_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class PostSummary(BaseModel):
    """Lightweight version for paginated feed — excludes main_content"""
    id: str
    title: str
    summary: str
    img_url: Optional[str]
    focus_areas: List[str]
    published_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class PostRead(BaseModel):
    id: UUID
    title: str
    slug: str
    summary: str
    content: str
    cover_image: Optional[str] = None
    source_urls: List[str] = []
    tags: List[str] = []
    category: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PostSummary(BaseModel):
    """Lightweight version for paginated feed"""
    id: UUID
    title: str
    slug: str
    summary: str
    cover_image: Optional[str] = None
    tags: List[str] = []
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

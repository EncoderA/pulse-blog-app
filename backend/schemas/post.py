from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PostCreate(BaseModel):
    title: str
    slug: str
    summary: str
    content: str
    cover_image: Optional[str] = None
    source_urls: List[str] = []
    tags: List[str] = []
    category: Optional[str] = None


class PostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None


class PostRead(BaseModel):
    id: str
    title: str
    slug: str
    summary: str
    content: str
    cover_image: Optional[str] = None
    tags: List[str] = []
    category: Optional[str] = None
    source_urls: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

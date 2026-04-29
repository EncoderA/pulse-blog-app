from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, TSVECTOR
from sqlmodel import SQLModel, Field


class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    slug: str = Field(unique=True, index=True)
    summary: str
    content: str = Field(sa_column=Column(Text, nullable=False))
    cover_image: Optional[str] = None
    source_urls: List[str] = Field(
        default=[], sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
    tags: List[str] = Field(
        default=[], sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
    category: Optional[str] = None
    status: str = "published"  # always published on insert
    search_vector: Optional[str] = Field(
        default=None, sa_column=Column(TSVECTOR)
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String, Text
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.dialects.postgresql import TSVECTOR

class Post(SQLModel, table=True):
    __tablename__ = "post"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=255)
    slug: str = Field(max_length=255)
    summary: str = Field(max_length=1000)
    content: str = Field(sa_column=Column(Text))
    cover_image: Optional[str] = Field(default=None, max_length=255)
    source_urls: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    tags: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    category: Optional[str] = Field(default=None, max_length=255)
    status: str = Field(default="published", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    search_vector: Optional[str] = Field(default=None, sa_column=Column(TSVECTOR))

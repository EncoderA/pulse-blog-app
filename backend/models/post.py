from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime

class Post(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    summary: str                                   # short summary
    main_content: str                              # full HTML content
    img_url: Optional[str] = None                 # cover image URL
    article_source_urls: List[str] = Field(
        default=[], sa_column=Column(ARRAY(String))
    )
    focus_areas: List[str] = Field(
        default=[], sa_column=Column(ARRAY(String))
    )
    published_date: Optional[datetime] = None     # date from external source
    external_id: Optional[str] = Field(           # external post identifier
        default=None, unique=True, index=True     # used for deduplication
    )
    search_vector: Optional[str] = None           # tsvector, managed by DB trigger
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import SmallInteger
from typing import Optional
from datetime import datetime


class TimelineComment(SQLModel, table=True):
    __tablename__ = "timeline_comments"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="timeline_posts.id")

    comment_text: str
    commenter_name: Optional[str] = Field(default=None, max_length=150)
    commenter_designation: Optional[str] = Field(default=None, max_length=150)
    commenter_image_url: Optional[str] = None

    is_mock: bool = Field(default=True)
    display_order: int = Field(
        default=0,
        sa_column=Column(SmallInteger, nullable=True, server_default="0")
    )
    created_at: Optional[datetime] = Field(default=None)

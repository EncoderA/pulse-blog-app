from sqlmodel import SQLModel, Field, Column
from sqlalchemy import SmallInteger
from typing import Optional
from datetime import datetime


class TimelineEvent(SQLModel, table=True):
    __tablename__ = "timeline_events"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="timeline_posts.id")

    event_time: Optional[datetime] = None
    event_title: Optional[str] = None
    event_content: Optional[str] = None
    event_image_url: Optional[str] = None
    sequence_order: int = Field(
        default=0,
        sa_column=Column(SmallInteger, nullable=False, server_default="0")
    )

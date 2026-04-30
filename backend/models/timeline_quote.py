from sqlmodel import SQLModel, Field, Column
from sqlalchemy import SmallInteger
from typing import Optional


class TimelineQuote(SQLModel, table=True):
    __tablename__ = "timeline_quotes"

    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="timeline_posts.id")

    quote_text: str
    attributed_to: Optional[str] = None
    display_order: int = Field(
        default=0,
        sa_column=Column(SmallInteger, nullable=True, server_default="0")
    )

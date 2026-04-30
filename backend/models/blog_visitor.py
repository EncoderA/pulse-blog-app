import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class BlogVisitor(SQLModel, table=True):
    __tablename__ = "blog_visitor"

    visit_date: datetime.date = Field(primary_key=True)
    blog_id: Optional[str] = Field(default=None, primary_key=True)
    visitor_count: int = Field(default=0)

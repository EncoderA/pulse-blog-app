import datetime
from sqlmodel import SQLModel, Field


class WebVisitor(SQLModel, table=True):
    __tablename__ = "web_visitor"

    date: datetime.date = Field(primary_key=True)
    visitor_count: int = Field(default=0)

from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class AppVisit(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    visited_at: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None

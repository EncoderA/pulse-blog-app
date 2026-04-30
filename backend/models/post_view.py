from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class PostView(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    post_id: str
    viewed_at: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None

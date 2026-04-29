from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class PostView(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    post_id: UUID = Field(foreign_key="post.id")
    viewed_at: datetime = Field(default_factory=datetime.utcnow)
    user_agent: Optional[str] = None

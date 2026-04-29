from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    password_hash: Optional[str] = None  # None for OAuth users
    avatar: Optional[str] = None
    role: str = "admin"  # only one role — admin
    provider: str = "local"  # "local" | "google" | "github"
    created_at: datetime = Field(default_factory=datetime.utcnow)

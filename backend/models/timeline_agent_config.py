from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String
from typing import Optional, List
from datetime import datetime


class TimelineAgentConfig(SQLModel, table=True):
    __tablename__ = "timeline_agent_configs"

    id: Optional[int] = Field(default=None, primary_key=True)

    context_name: str = Field(max_length=100)
    custom_instructions: Optional[str] = None
    focus_topics: Optional[List[str]] = Field(
        default=None, sa_column=Column(ARRAY(String))
    )
    tone: str = Field(default="neutral", max_length=30)
    analysis_depth: str = Field(default="standard", max_length=20)
    llm_model_override: Optional[str] = Field(default=None, max_length=100)

    auto_enrich: bool = Field(default=True)
    active: bool = Field(default=True)

    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)

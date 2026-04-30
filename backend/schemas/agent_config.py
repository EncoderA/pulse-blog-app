from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AgentConfigBase(BaseModel):
    context_name: str
    custom_instructions: Optional[str] = None
    focus_topics: Optional[List[str]] = None
    tone: str = "neutral"
    analysis_depth: str = "standard"
    llm_model_override: Optional[str] = None
    auto_enrich: bool = True
    active: bool = True


class AgentConfigCreate(AgentConfigBase):
    pass


class AgentConfigUpdate(BaseModel):
    context_name: Optional[str] = None
    custom_instructions: Optional[str] = None
    focus_topics: Optional[List[str]] = None
    tone: Optional[str] = None
    analysis_depth: Optional[str] = None
    llm_model_override: Optional[str] = None
    auto_enrich: Optional[bool] = None
    active: Optional[bool] = None


class AgentConfigRead(AgentConfigBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PostRead(BaseModel):
    Id: int
    Title: Optional[str] = None
    Short_Summary: Optional[str] = None

    Date: Optional[datetime] = None
    Content_Length: Optional[int] = None
    Source_Url: Optional[str] = None
    Tags: Optional[str] = None

    Background: Optional[str] = None
    News: Optional[str] = None
    Highlights: Optional[str] = None
    Impact: Optional[str] = None
    Whats_Next: Optional[str] = None

    Focus_Area: Optional[str] = None
    Overview: Optional[str] = None
    Impacts: Optional[str] = None

    Image_Url: Optional[List[str]] = None

    class Config:
        from_attributes = True

class PostSummary(BaseModel):
    """Lightweight version for paginated feed"""
    Id: int
    Title: Optional[str] = None
    Short_Summary: Optional[str] = None
    Date: Optional[datetime] = None
    Focus_Area: Optional[str] = None
    Image_Url: Optional[List[str]] = None

    class Config:
        from_attributes = True

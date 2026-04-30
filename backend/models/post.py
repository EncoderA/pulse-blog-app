from sqlmodel import SQLModel, Field, Column
from sqlalchemy import ARRAY, String, DateTime
from typing import Optional, List
from datetime import datetime

class Post(SQLModel, table=True):
    __tablename__ = "posts"
    
    Id: Optional[int] = Field(default=None, primary_key=True)
    Title: Optional[str] = Field(default=None, max_length=150)
    Short_Summary: Optional[str] = Field(default=None, max_length=300)

    Date: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    Content_Length: Optional[int] = None
    Source_Url: Optional[str] = Field(default=None, max_length=255)
    Tags: Optional[str] = Field(default=None, max_length=200)

    Background: Optional[str] = Field(default=None, max_length=300)
    News: Optional[str] = Field(default=None, max_length=300)
    Highlights: Optional[str] = Field(default=None, max_length=300)
    Impact: Optional[str] = Field(default=None, max_length=150)
    Whats_Next: Optional[str] = Field(default=None, max_length=150)

    Focus_Area: Optional[str] = Field(default=None, max_length=200)
    Overview: Optional[str] = Field(default=None, max_length=200)
    Impacts: Optional[str] = Field(default=None, max_length=200)

    Image_Url: Optional[List[str]] = Field(default=[], sa_column=Column(ARRAY(String(255))))

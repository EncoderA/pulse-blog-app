from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"

    Id = Column(Integer, primary_key=True, index=True)
    Title = Column(String(150))
    Short_Summary = Column(String(300))
    Date = Column(TIMESTAMP)
    Content_Length = Column(Integer)
    Source_Url = Column(String(255))
    Tags = Column(String(200))

    Background = Column(String(300))
    News = Column(String(300))
    Highlights = Column(String(300))
    Impact = Column(String(150))
    Whats_Next = Column(String(150))

    Focus_Area = Column(String(200))
    Overview = Column(String(200))
    Impacts = Column(String(200))

    Image_Url = Column(ARRAY(String))
from sqlmodel import create_engine
from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

def create_db_and_tables():
    from sqlmodel import SQLModel
    # Ensure models are imported before creating tables
    import models.post
    import models.web_visitor
    import models.blog_visitor
    SQLModel.metadata.create_all(engine)

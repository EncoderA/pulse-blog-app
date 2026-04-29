from sqlmodel import create_engine
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_db_and_tables():
    from sqlmodel import SQLModel
    # Ensure models are imported before creating tables
    import models.post
    import models.post_view
    SQLModel.metadata.create_all(engine)

from sqlmodel import create_engine
from core.config import settings

engine = create_engine(settings.DATABASE_URL)

def create_db_and_tables():
    from sqlmodel import SQLModel
    # Ensure models are imported before creating tables
    import models.post
    import models.web_visitor
    import models.blog_visitor
    import models.post_view
    import models.app_visit
    import models.timeline_post
    import models.timeline_event
    import models.timeline_quote
    import models.timeline_comment
    import models.timeline_agent_config
    SQLModel.metadata.create_all(engine)

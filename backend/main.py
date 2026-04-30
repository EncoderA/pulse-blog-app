from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import datetime

from core.config import settings
from core.database import create_db_and_tables, engine
from routers import auth, posts, admin, external
from services.ingest import ingest_posts
from dependencies import get_db
from models.web_visitor import WebVisitor
from models.blog_visitor import BlogVisitor

scheduler = AsyncIOScheduler()

async def ingest_job():
    with Session(engine) as db:
        await ingest_posts(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_db_and_tables()
    scheduler.add_job(ingest_job, "interval", hours=3, id="ingest_posts")
    scheduler.start()
    yield
    # Shutdown
    scheduler.shutdown()

app = FastAPI(title="News Blog API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(external.router, prefix="/public/analytics", tags=["public-analytics"])


@app.post("/analytics/web-visit", tags=["analytics"])
def record_web_visit(db: Session = Depends(get_db)):
    """Increment the web visitor count for today."""
    today = datetime.date.today()
    row = db.exec(select(WebVisitor).where(WebVisitor.date == today)).first()
    if row:
        row.visitor_count += 1
        db.add(row)
    else:
        db.add(WebVisitor(date=today, visitor_count=1))
    db.commit()
    return {"status": "success", "date": today}


@app.post("/analytics/blog-visit/{blog_id}", tags=["analytics"])
def record_blog_visit(blog_id: str, db: Session = Depends(get_db)):
    """Increment the blog visitor count for today and the given blog_id."""
    today = datetime.date.today()
    row = db.exec(
        select(BlogVisitor).where(
            BlogVisitor.visit_date == today,
            BlogVisitor.blog_id == blog_id,
        )
    ).first()
    if row:
        row.visitor_count += 1
        db.add(row)
    else:
        db.add(BlogVisitor(visit_date=today, blog_id=blog_id, visitor_count=1))
    db.commit()
    return {"status": "success", "date": today, "blog_id": blog_id}

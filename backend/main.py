from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session
from contextlib import asynccontextmanager

from core.config import settings
from core.database import create_db_and_tables, engine
from routers import auth, posts, admin
from services.ingest import ingest_posts

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

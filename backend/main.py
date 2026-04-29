from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import create_db_and_tables
from routers import auth, posts, admin, agent

app = FastAPI(title="Pulse AI Blog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,  # required for cookies to work cross-origin
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Import models so SQLModel metadata is populated
    import models  # noqa: F401
    create_db_and_tables()


app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(admin.router)
app.include_router(agent.router)

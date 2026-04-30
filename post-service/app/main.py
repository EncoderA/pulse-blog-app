# from fastapi import FastAPI
# from app.api.routes import ingest

# app = FastAPI()

# app.include_router(ingest.router)

# from fastapi import FastAPI
# from dotenv import load_dotenv
# import os

# load_dotenv()

# from app.api.routes import ingest

# app = FastAPI()

# app.include_router(ingest.router)
# from fastapi import FastAPI
# from dotenv import load_dotenv

# load_dotenv()

# from app.api.routes import ingest

# app = FastAPI()
# app.include_router(ingest.router)

from fastapi import FastAPI
from app.api.routes import ingest
from app.db.database import engine
from app.db.models import Base

app = FastAPI()

# 🔥 THIS LINE CREATES TABLES IN NEON
Base.metadata.create_all(bind=engine)

app.include_router(ingest.router)
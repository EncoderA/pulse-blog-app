# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session
# # from app.db.database import get_db
# # from app.services.ingest_service import ingest_news_pipeline

# # router = APIRouter()


# # # ✅ POST → fetch from KB (JSON now) + insert into DB
# # @router.post("/ingest")
# # def ingest_news(db: Session = Depends(get_db)):
# #     return ingest_news_pipeline(db)

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.db.database import get_db

# from app.services.ingest_service import ingest_news_pipeline
# from app.services.kb_service import fetch_kb_posts

# router = APIRouter()


# # -------------------------------
# # POST → INSERT INTO OUR DB
# # -------------------------------
# @router.post("/ingest")
# def ingest_news(db: Session = Depends(get_db)):
#     return ingest_news_pipeline(db)


# # -------------------------------
# # GET → FETCH FROM KB (JSON NOW)
# # -------------------------------
# @router.get("/kb-posts")
# def get_kb_posts():
#     return fetch_kb_posts()

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from app.db.database import get_db

# from app.services.ingest_service import ingest_news_pipeline
# from app.services.kb_db_service import (
#     fetch_kb_posts_from_db,
#     get_tables,
#     get_columns
# )

# router = APIRouter()


# # POST → Your DB
# @router.post("/ingest")
# def ingest_news(db: Session = Depends(get_db)):
#     return ingest_news_pipeline(db)


# # GET → TEMP check connection
# @router.get("/kb-posts")
# async def get_kb_posts():
#     return await fetch_kb_posts_from_db()


# # DEBUG → get tables
# @router.get("/kb-tables")
# async def kb_tables():
#     return await get_tables()


# # DEBUG → get columns
# @router.get("/kb-columns/{table_name}")
# async def kb_columns(table_name: str):
#     return await get_columns(table_name)

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.db.database import get_db

# # ✅ Import BOTH services
# from app.services.ingest_service import ingest_from_kb
# from app.services.kb_db_service import fetch_kb_posts_from_db

# router = APIRouter()


# # 🔹 POST → insert into YOUR DB
# @router.post("/ingest")
# async def ingest_news(db: Session = Depends(get_db)):
#     return await ingest_from_kb(db)


# # 🔹 GET → fetch from KB DB (NOT YOUR DB)
# @router.get("/kb-posts")
# async def get_kb_posts():
#     return await fetch_kb_posts_from_db()

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.ingest_service import ingest_from_kb
from app.services.kb_db_service import fetch_kb_posts_from_db

router = APIRouter()


# 🔹 GET → fetch from KB DB
@router.get("/kb-posts")
async def get_kb_posts():
    return await fetch_kb_posts_from_db()


# 🔹 POST → store into YOUR DB
@router.post("/ingest")
async def ingest_news(db: Session = Depends(get_db)):
    return await ingest_from_kb(db)
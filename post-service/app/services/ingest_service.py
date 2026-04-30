# import json
# from sqlalchemy.orm import Session
# from datetime import datetime
# from sqlalchemy import text


# # -------------------------------
# # 1️⃣ FETCH DATA (KB SOURCE)
# # -------------------------------
# def fetch_kb_data_from_file():
#     with open("app/data/kb_data.json", "r", encoding="utf-8") as f:
#         data = json.load(f)

#     return data.get("items", [])


# # -------------------------------
# # 2️⃣ TRANSFORM DATA
# # -------------------------------
# def transform_kb_item(item):

#     title = item.get("title")
#     summary = item.get("summary_raw")
#     raw_date = item.get("published_at")
#     content = item.get("content_raw")
#     images = item.get("images") or []

#     # 🔹 Trim for DB limits
#     title = title[:150] if title else None
#     summary = summary[:300] if summary else None

#     # 🔹 Date parsing
#     parsed_date = None
#     if raw_date:
#         try:
#             parsed_date = datetime.fromisoformat(raw_date)
#         except:
#             parsed_date = None

#     # 🔹 Derived fields
#     content_length = len(content) if content else 0
#     image_url = [images[0]] if images else []

#     return {
#         "Title": title,
#         "Short_Summary": summary,
#         "Date": parsed_date,
#         "Content_Length": content_length,
#         "Source_Url": None,
#         "Tags": "",
#         "Background": "",
#         "News": "",
#         "Highlights": "",
#         "Impact": "",
#         "Whats_Next": "",
#         "Focus_Area": "",
#         "Overview": summary[:200] if summary else "",
#         "Impacts": "",
#         "Image_Url": image_url
#     }


# # -------------------------------
# # 3️⃣ INSERT INTO DB
# # -------------------------------
# def insert_post(db: Session, record: dict):

#     db.execute(
#         text("""
#         INSERT INTO posts
#         ("Title","Short_Summary","Date","Content_Length",
#          "Source_Url","Tags",
#          "Background","News","Highlights","Impact","Whats_Next",
#          "Focus_Area","Overview","Impacts","Image_Url")
#         VALUES
#         (:Title,:Short_Summary,:Date,:Content_Length,
#          :Source_Url,:Tags,
#          :Background,:News,:Highlights,:Impact,:Whats_Next,
#          :Focus_Area,:Overview,:Impacts,:Image_Url)
#         """),
#         record
#     )


# # -------------------------------
# # 4️⃣ MAIN PIPELINE (USED BY POST API)
# # -------------------------------
# def ingest_news_pipeline(db: Session):

#     items = fetch_kb_data_from_file()

#     inserted_count = 0

#     for item in items:
#         record = transform_kb_item(item)
#         insert_post(db, record)
#         inserted_count += 1

#     db.commit()

#     return {
#         "message": "Data fetched (JSON as KB) and inserted into DB",
#         "count": inserted_count
#     }


# import asyncio
# from sqlalchemy.orm import Session
# from datetime import datetime
# from sqlalchemy import text

# from app.services.kb_db_service import fetch_kb_posts_from_db


# def ingest_from_kb(db: Session):

#     # 🔹 GET DATA FROM KB DB
#     kb_data = asyncio.run(fetch_kb_posts_from_db())

#     inserted_count = 0

#     for item in kb_data:

#         title = (item.get("title") or "")[:150]
#         summary = (item.get("summary") or "")[:300]
#         content = item.get("content") or ""
#         raw_date = item.get("published_at")
#         source_url = item.get("source_url")

#         # 🔹 DATE PARSE
#         parsed_date = None
#         if raw_date:
#             try:
#                 parsed_date = datetime.fromisoformat(raw_date)
#             except:
#                 parsed_date = None

#         # 🔹 DERIVED
#         content_length = len(content)

#         # 🔹 INSERT RECORD
#         record = {
#             "Title": title,
#             "Short_Summary": summary,
#             "Date": parsed_date,
#             "Content_Length": content_length,
#             "Source_Url": source_url,

#             "Tags": "",
#             "Background": "",
#             "News": content[:300],   # short content
#             "Highlights": "",
#             "Impact": "",
#             "Whats_Next": "",
#             "Focus_Area": "",
#             "Overview": summary[:200],
#             "Impacts": "",
#             "Image_Url": []
#         }

#         db.execute(
#             text("""
#             INSERT INTO posts
#             ("Title","Short_Summary","Date","Content_Length",
#              "Source_Url","Tags",
#              "Background","News","Highlights","Impact","Whats_Next",
#              "Focus_Area","Overview","Impacts","Image_Url")
#             VALUES
#             (:Title,:Short_Summary,:Date,:Content_Length,
#              :Source_Url,:Tags,
#              :Background,:News,:Highlights,:Impact,:Whats_Next,
#              :Focus_Area,:Overview,:Impacts,:Image_Url)
#             """),
#             record
#         )

#         inserted_count += 1

#     db.commit()

#     return {
#         "message": "KB data inserted into your DB",
#         "count": inserted_count
#     }



# import asyncio
# from sqlalchemy.orm import Session
# from datetime import datetime
# from sqlalchemy import text

# from app.services.kb_db_service import fetch_kb_posts_from_db


# async def ingest_from_kb(db: Session):

#     # 🔹 GET DATA FROM KB DB
#     kb_data = await fetch_kb_posts_from_db()

#     inserted_count = 0
#     skipped_count = 0

#     for item in kb_data:

#         title = (item.get("title") or "")[:150]
#         summary = (item.get("summary") or "")[:300]
#         content = item.get("content") or ""
#         raw_date = item.get("published_at")
#         source_url = item.get("source_url")

#         # 🔴 IMPORTANT: SKIP IF SOURCE_URL IS NULL
#         if not source_url:
#             skipped_count += 1
#             continue

#         # 🔥 NEW: DUPLICATE CHECK
#         existing = db.execute(
#             text('SELECT "Id" FROM posts WHERE "Source_Url" = :url'),
#             {"url": source_url}
#         ).fetchone()

#         if existing:
#             skipped_count += 1
#             continue

#         # 🔹 DATE PARSE
#         parsed_date = None
#         if raw_date:
#             try:
#                 parsed_date = datetime.fromisoformat(raw_date)
#             except:
#                 parsed_date = None

#         # 🔹 DERIVED
#         content_length = len(content)

#         # 🔹 INSERT RECORD
#         record = {
#             "Title": title,
#             "Short_Summary": summary,
#             "Date": parsed_date,
#             "Content_Length": content_length,
#             "Source_Url": source_url,

#             "Tags": "",
#             "Background": "",
#             "News": content[:300],
#             "Highlights": "",
#             "Impact": "",
#             "Whats_Next": "",
#             "Focus_Area": "",
#             "Overview": summary[:200],
#             "Impacts": "",
#             "Image_Url": []
#         }

#         db.execute(
#             text("""
#             INSERT INTO posts
#             ("Title","Short_Summary","Date","Content_Length",
#              "Source_Url","Tags",
#              "Background","News","Highlights","Impact","Whats_Next",
#              "Focus_Area","Overview","Impacts","Image_Url")
#             VALUES
#             (:Title,:Short_Summary,:Date,:Content_Length,
#              :Source_Url,:Tags,
#              :Background,:News,:Highlights,:Impact,:Whats_Next,
#              :Focus_Area,:Overview,:Impacts,:Image_Url)
#             """),
#             record
#         )

#         inserted_count += 1

#     db.commit()

#     return {
#         "message": "KB data processed",
#         "inserted": inserted_count,
#         "skipped_duplicates": skipped_count
#     }


# import asyncio
# import logging
# from sqlalchemy.orm import Session
# from datetime import datetime
# from sqlalchemy import text
# from dateutil import parser

# from app.services.kb_db_service import fetch_kb_posts_from_db

# logging.basicConfig(level=logging.INFO)


# async def ingest_from_kb(db: Session):

#     # 🔹 FETCH DATA FROM KB
#     try:
#         kb_data = await fetch_kb_posts_from_db()
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Failed to fetch from KB DB: {str(e)}"
#         }

#     inserted_count = 0
#     skipped_count = 0

#     for item in kb_data:

#         try:
#             # 🔹 BASIC VALIDATION
#             if not item.get("title") or not item.get("source_url"):
#                 skipped_count += 1
#                 continue

#             title = item.get("title")[:150]
#             summary = (item.get("summary") or "")[:300]
#             content = item.get("content") or ""
#             raw_date = item.get("published_at")
#             source_url = item.get("source_url")

#             # 🔹 DUPLICATE CHECK
#             existing = db.execute(
#                 text('SELECT "Id" FROM posts WHERE "Source_Url" = :url'),
#                 {"url": source_url}
#             ).fetchone()

#             if existing:
#                 skipped_count += 1
#                 continue

#             # 🔹 SAFE DATE PARSE
#             parsed_date = None
#             if raw_date:
#                 try:
#                     parsed_date = parser.parse(raw_date)
#                 except Exception:
#                     parsed_date = None

#             # 🔹 DERIVED
#             content_length = len(content)

#             record = {
#                 "Title": title,
#                 "Short_Summary": summary,
#                 "Date": parsed_date,
#                 "Content_Length": content_length,
#                 "Source_Url": source_url,

#                 "Tags": "",
#                 "Background": "",
#                 "News": content[:300],
#                 "Highlights": "",
#                 "Impact": "",
#                 "Whats_Next": "",
#                 "Focus_Area": "",
#                 "Overview": summary[:200],
#                 "Impacts": "",
#                 "Image_Url": []
#             }

#             db.execute(
#                 text("""
#                 INSERT INTO posts
#                 ("Title","Short_Summary","Date","Content_Length",
#                  "Source_Url","Tags",
#                  "Background","News","Highlights","Impact","Whats_Next",
#                  "Focus_Area","Overview","Impacts","Image_Url")
#                 VALUES
#                 (:Title,:Short_Summary,:Date,:Content_Length,
#                  :Source_Url,:Tags,
#                  :Background,:News,:Highlights,:Impact,:Whats_Next,
#                  :Focus_Area,:Overview,:Impacts,:Image_Url)
#                 """),
#                 record
#             )

#             inserted_count += 1

#             logging.info(f"Inserted: {title}")

#         except Exception as e:
#             logging.error(f"Error processing item: {str(e)}")
#             skipped_count += 1
#             continue

#     db.commit()

#     return {
#         "status": "success",
#         "inserted": inserted_count,
#         "skipped": skipped_count
#     }


import logging
import os
import re
from sqlalchemy.orm import Session
from sqlalchemy import text
from dateutil import parser

from app.services.kb_db_service import fetch_kb_posts_from_db

logging.basicConfig(level=logging.INFO)

if not os.getenv("KB_DB_URL"):
    raise Exception("KB_DB_URL missing")

if not os.getenv("POST_DB_URL"):
    raise Exception("POST_DB_URL missing")


def _slugify(title: str) -> str:
    """Generate a URL-safe slug from a title string."""
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    return s[:200]


def _parse_file_content(file_content: str) -> tuple:
    """
    Parse the file_content column from cleaned_articles.
    Format: "title | 2-sentence summary | keywords: k1, k2 | entities: e1, e2"
    Returns (tags: list[str], entities: list[str])
    """
    tags: list = []
    entities: list = []
    for part in (file_content or "").split(" | "):
        if part.startswith("keywords: "):
            tags = [k.strip() for k in part[len("keywords: "):].split(",") if k.strip()]
        elif part.startswith("entities: "):
            entities = [e.strip() for e in part[len("entities: "):].split(",") if e.strip()]
    return tags, entities


def _first_sentences(text: str, n: int) -> str:
    """Return the first n sentences of text, joined with a space."""
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:n])


async def ingest_from_kb(db: Session):

    try:
        kb_data = await fetch_kb_posts_from_db()
    except Exception as e:
        logging.error(f"KB fetch failed: {str(e)}")
        return {"status": "error", "message": "Failed to fetch data from KB"}

    inserted_count = 0
    skipped_count = 0

    for item in kb_data:
        try:
            if not item.get("title") or not item.get("source_url"):
                skipped_count += 1
                continue

            title = item["title"][:150]
            summary = (item.get("summary") or "")[:300]
            content = item.get("content") or ""
            raw_date = item.get("published_at")
            source_url = item["source_url"]
            file_content = item.get("file_content") or ""
            primary_image = item.get("primary_image")
            article_id = item.get("article_id") or ""

            # Duplicate check on posts table
            existing = db.execute(
                text('SELECT "Id" FROM posts WHERE "Source_Url" = :url'),
                {"url": source_url}
            ).fetchone()
            if existing:
                skipped_count += 1
                continue

            # Date parsing
            parsed_date = None
            if raw_date:
                try:
                    parsed_date = parser.parse(raw_date)
                except Exception:
                    parsed_date = None

            content_length = len(content)
            tags, entities = _parse_file_content(file_content)
            slug = _slugify(title)
            short_summary = _first_sentences(content, 2)
            quick_take = _first_sentences(summary, 1)

            # INSERT into posts
            db.execute(
                text("""
                INSERT INTO posts
                ("Title","Short_Summary","Date","Content_Length",
                 "Source_Url","Tags",
                 "Background","News","Highlights","Impact","Whats_Next",
                 "Focus_Area","Overview","Impacts","Image_Url")
                VALUES
                (:Title,:Short_Summary,:Date,:Content_Length,
                 :Source_Url,:Tags,
                 :Background,:News,:Highlights,:Impact,:Whats_Next,
                 :Focus_Area,:Overview,:Impacts,:Image_Url)
                """),
                {
                    "Title": title,
                    "Short_Summary": summary,
                    "Date": parsed_date,
                    "Content_Length": content_length,
                    "Source_Url": source_url,
                    "Tags": ", ".join(tags),
                    "Background": "",
                    "News": content[:300],
                    "Highlights": "",
                    "Impact": "",
                    "Whats_Next": "",
                    "Focus_Area": ", ".join(entities),
                    "Overview": summary[:200],
                    "Impacts": "",
                    "Image_Url": [primary_image] if primary_image else [],
                }
            )

            # UPSERT into timeline_posts (skip if article_id already exists)
            db.execute(
                text("""
                INSERT INTO timeline_posts
                    (article_id, kb_source, slug, title, short_summary, published_at,
                     content_length, source_url, tags, focus_area, quick_take,
                     primary_image_url, ingest_status)
                VALUES
                    (:article_id, :kb_source, :slug, :title, :short_summary, :published_at,
                     :content_length, :source_url, :tags, :focus_area, :quick_take,
                     :primary_image_url, 'pending')
                ON CONFLICT (article_id) DO NOTHING
                """),
                {
                    "article_id": article_id,
                    "kb_source": "",
                    "slug": slug,
                    "title": title,
                    "short_summary": short_summary[:500] if short_summary else summary,
                    "published_at": parsed_date,
                    "content_length": content_length,
                    "source_url": source_url,
                    "tags": tags,
                    "focus_area": entities,
                    "quick_take": quick_take[:500] if quick_take else None,
                    "primary_image_url": primary_image,
                }
            )

            # INSERT one timeline_event row (full content as the single event)
            db.execute(
                text("""
                INSERT INTO timeline_events
                    (post_id, event_time, event_title, event_content, sequence_order)
                SELECT id, :event_time, :event_title, :event_content, 1
                FROM timeline_posts
                WHERE article_id = :article_id
                ON CONFLICT DO NOTHING
                """),
                {
                    "article_id": article_id,
                    "event_time": parsed_date,
                    "event_title": title,
                    "event_content": content[:2000] if content else "",
                }
            )

            inserted_count += 1
            logging.info(f"Inserted: {title}")

        except Exception as e:
            logging.error(f"Error processing item: {str(e)}")
            skipped_count += 1
            continue

    db.commit()

    return {
        "status": "success",
        "inserted": inserted_count,
        "skipped": skipped_count,
    }
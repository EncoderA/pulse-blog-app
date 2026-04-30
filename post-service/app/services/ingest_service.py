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
from sqlalchemy.orm import Session
from sqlalchemy import text
from dateutil import parser

from app.services.kb_db_service import fetch_kb_posts_from_db

# 🔹 LOGGING SETUP
logging.basicConfig(level=logging.INFO)


# 🔹 ENV VALIDATION (runs when file loads)
if not os.getenv("KB_DB_URL"):
    raise Exception("KB_DB_URL missing")

if not os.getenv("POST_DB_URL"):
    raise Exception("POST_DB_URL missing")


async def ingest_from_kb(db: Session):

    # 🔹 FETCH DATA
    try:
        kb_data = await fetch_kb_posts_from_db()
    except Exception as e:
        logging.error(f"KB fetch failed: {str(e)}")
        return {
            "status": "error",
            "message": "Failed to fetch data from KB"
        }

    inserted_count = 0
    skipped_count = 0

    for item in kb_data:

        try:
            # 🔹 DATA VALIDATION
            if not item.get("title") or not item.get("source_url"):
                skipped_count += 1
                continue

            title = item.get("title")[:150]
            summary = (item.get("summary") or "")[:300]
            content = item.get("content") or ""
            raw_date = item.get("published_at")
            source_url = item.get("source_url")

            # 🔹 DUPLICATE CHECK
            existing = db.execute(
                text('SELECT "Id" FROM posts WHERE "Source_Url" = :url'),
                {"url": source_url}
            ).fetchone()

            if existing:
                skipped_count += 1
                continue

            # 🔹 SAFE DATE PARSING
            parsed_date = None
            if raw_date:
                try:
                    parsed_date = parser.parse(raw_date)
                except Exception:
                    parsed_date = None

            # 🔹 DERIVED
            content_length = len(content)

            record = {
                "Title": title,
                "Short_Summary": summary,
                "Date": parsed_date,
                "Content_Length": content_length,
                "Source_Url": source_url,

                "Tags": "",
                "Background": "",
                "News": content[:300],
                "Highlights": "",
                "Impact": "",
                "Whats_Next": "",
                "Focus_Area": "",
                "Overview": summary[:200],
                "Impacts": "",
                "Image_Url": []
            }

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
                record
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
        "skipped": skipped_count
    }
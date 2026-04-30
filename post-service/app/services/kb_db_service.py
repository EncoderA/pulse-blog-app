# import asyncpg
# import os


# # STEP 1: Get all tables (DEBUG)
# async def get_tables():

#     conn = await asyncpg.connect(os.getenv("KB_DB_URL"))

#     query = """
#         SELECT table_name 
#         FROM information_schema.tables
#         WHERE table_schema = 'public';
#     """

#     rows = await conn.fetch(query)
#     await conn.close()

#     return [row["table_name"] for row in rows]


# # STEP 2: Get columns of a table (DEBUG)
# async def get_columns(table_name: str):

#     conn = await asyncpg.connect(os.getenv("KB_DB_URL"))

#     query = """
#         SELECT column_name, data_type
#         FROM information_schema.columns
#         WHERE table_name = $1;
#     """

#     rows = await conn.fetch(query, table_name)
#     await conn.close()

#     return [{"column": r["column_name"], "type": r["data_type"]} for r in rows]


# # STEP 3: TEMP fetch (will fix later)
# async def fetch_kb_posts_from_db():

#     conn = await asyncpg.connect(os.getenv("KB_DB_URL"))

#     # ⚠️ TEMP SAFE QUERY (NO COLUMN ASSUMPTION)
#     query = """
#         SELECT *
#         FROM information_schema.tables
#         LIMIT 5;
#     """

#     rows = await conn.fetch(query)
#     await conn.close()

#     return [dict(row) for row in rows]


# import asyncpg
# import os


# async def fetch_kb_posts_from_db():

#     conn = await asyncpg.connect(
#         os.getenv("KB_DB_URL"),
#         ssl="require"   # IMPORTANT for Neon
#     )

#     # ✅ CLEANED_ARTICLES TABLE ACCESS
#     query = """
#         SELECT
#             title,
#             summary,
#             content,
#             published_at,
#             images
#         FROM cleaned_articles
#         ORDER BY published_at DESC
#         LIMIT 50;
#     """

#     rows = await conn.fetch(query)
#     await conn.close()

#     result = []

#     for row in rows:
#         result.append({
#             "title": row.get("title"),
#             "summary": row.get("summary"),
#             "published_at": str(row.get("published_at")),
#             "content": row.get("content"),
#             "image": row.get("images")[0] if row.get("images") else None
#         })

#     return result

# import asyncpg
# import os


# async def fetch_kb_posts_from_db():
#     try:
#         conn = await asyncpg.connect(
#             os.getenv("KB_DB_URL"),
#             ssl="require"
#         )

#         # ✅ STEP 2: GET COLUMNS
#         query = """
#         SELECT *
#         FROM information_schema.columns
#         WHERE table_name = 'cleaned_articles';
#         """

#         rows = await conn.fetch(query)

#         await conn.close()

#         return {
#             "status": "connected",
#             "columns": [row["column_name"] for row in rows]
#         }

#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }

# import asyncpg
# import os


# async def fetch_kb_posts_from_db():
#     try:
#         conn = await asyncpg.connect(
#             os.getenv("KB_DB_URL"),
#             ssl="require"
#         )

#         # ✅ FINAL WORKING QUERY
#         query = """
#         SELECT
#             *
#         FROM cleaned_articles
#         ORDER BY published_at DESC
#         LIMIT 50;
#         """

#         rows = await conn.fetch(query)

#         await conn.close()

#         result = []

#         for row in rows:
#             result.append({
#                 "title": row["title"],
#                 "summary": row["summary_raw"],
#                 "content": row["content_raw"],
#                 "published_at": str(row["published_at"]),
#                 "source_url": row["source_url"]
#             })

#         return result

#     except Exception as e:
#         return {
#             "status": "error",
#             "message": str(e)
#         }

import asyncpg
import os


async def fetch_kb_posts_from_db():

    conn = await asyncpg.connect(
        os.getenv("KB_DB_URL"),
        ssl=os.getenv("KB_DB_SSLMODE", "require")
    )

    query = """
        SELECT
            ca.article_id,
            ca.title,
            ca.summary_raw,
            ca.content_raw,
            ca.published_at,
            ca.source_url,
            ca.file_content,
            (
                SELECT image_url
                FROM cleaned_article_images
                WHERE article_id = ca.article_id
                LIMIT 1
            ) AS primary_image
        FROM cleaned_articles ca
        ORDER BY ca.published_at DESC
        LIMIT 100;
    """

    rows = await conn.fetch(query)
    await conn.close()

    result = []

    for row in rows:
        result.append({
            "article_id": row["article_id"],
            "title": row["title"],
            "summary": row["summary_raw"],
            "content": row["content_raw"],
            "published_at": str(row["published_at"]),
            "source_url": row["source_url"],
            "file_content": row["file_content"],
            "primary_image": row["primary_image"],
        })

    return result
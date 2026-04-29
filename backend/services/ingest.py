import httpx
from sqlmodel import Session, select
from models.post import Post
from core.config import settings

# ── PLACEHOLDERS ────────────────────────────────────────────────────────
# 1. Replace EXTERNAL_API_URL and EXTERNAL_API_KEY in .env once available
# 2. Update map_to_post() field names to match the real external schema
# 3. Update the deduplication key if external system uses something other
#    than an "id" field (currently stored as external_id)
# ────────────────────────────────────────────────────────────────────────

async def fetch_external_posts() -> list[dict]:
    """Call external API and return list of raw post dicts."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            settings.EXTERNAL_API_URL,
            headers={"Authorization": f"Bearer {settings.EXTERNAL_API_KEY}"}
        )
        response.raise_for_status()
        return response.json()   # ← adjust once real response shape is known

def map_to_post(raw: dict) -> Post:
    """
    Map raw external post to local Post model.
    ── UPDATE THESE FIELD NAMES once external schema is confirmed ──
    External field     →  Local field
    raw["title"]       →  title
    raw["summary"]     →  summary
    raw["date"]        →  published_date
    raw["urls"]        →  article_source_urls
    raw["focus_areas"] →  focus_areas
    raw["content"]     →  main_content  (HTML)
    raw["img_url"]     →  img_url
    raw["id"]          →  external_id   (used for deduplication)
    """
    return Post(
        title=raw.get("title", ""),
        summary=raw.get("summary", ""),
        main_content=raw.get("content", ""),
        img_url=raw.get("img_url", None),
        article_source_urls=raw.get("urls", []),
        focus_areas=raw.get("focus_areas", []),
        published_date=raw.get("date", None),
        external_id=str(raw.get("id", "")),
    )

async def ingest_posts(db: Session) -> dict:
    """
    Fetch from external API, skip already-stored posts
    (deduplicated by external_id), insert new ones.
    """
    raw_posts = await fetch_external_posts()
    new_count = 0

    for raw in raw_posts:
        external_id = str(raw.get("id", ""))
        if not external_id:
            continue

        existing = db.exec(
            select(Post).where(Post.external_id == external_id)
        ).first()
        if existing:
            continue

        post = map_to_post(raw)
        db.add(post)
        new_count += 1

    db.commit()
    return {"ingested": new_count}

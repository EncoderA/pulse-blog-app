import httpx
from sqlmodel import Session, select
from models.post import Post
from core.config import settings
import uuid

# ── PLACEHOLDERS ────────────────────────────────────────────────────────
# 1. Replace EXTERNAL_API_URL and EXTERNAL_API_KEY in .env once available
# 2. Update map_to_post() field names to match the real external schema
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
    """
    return Post(
        title=raw.get("title", ""),
        slug=raw.get("slug", str(uuid.uuid4())),
        summary=raw.get("summary", ""),
        content=raw.get("content", ""),
        cover_image=raw.get("cover_image", None),
        source_urls=raw.get("source_urls", []),
        tags=raw.get("tags", []),
        category=raw.get("category", None),
        status=raw.get("status", "published")
    )

async def ingest_posts(db: Session) -> dict:
    """
    Fetch from external API, skip already-stored posts
    insert new ones.
    """
    raw_posts = await fetch_external_posts()
    new_count = 0

    for raw in raw_posts:
        slug = raw.get("slug", "")
        if not slug:
            continue

        existing = db.exec(
            select(Post).where(Post.slug == slug)
        ).first()
        if existing:
            continue

        post = map_to_post(raw)
        db.add(post)
        new_count += 1

    db.commit()
    return {"ingested": new_count}

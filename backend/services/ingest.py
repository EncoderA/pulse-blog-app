import httpx
from sqlmodel import Session, select
from models.post import Post
from core.config import settings

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
        Title=raw.get("title", ""),
        Short_Summary=raw.get("summary", ""),
        Date=raw.get("date", None),
        Source_Url=raw.get("url", ""),
        Focus_Area=raw.get("focus_area", ""),
        Image_Url=[raw.get("img_url", "")] if raw.get("img_url") else [],
        Content_Length=0,
        Tags=raw.get("tags", ""),
        Background=raw.get("background", ""),
        News=raw.get("news", ""),
        Highlights=raw.get("highlights", ""),
        Impact=raw.get("impact", ""),
        Whats_Next=raw.get("whats_next", ""),
        Overview=raw.get("overview", ""),
        Impacts=raw.get("impacts", "")
    )

async def ingest_posts(db: Session) -> dict:
    """
    Fetch from external API, skip already-stored posts
    insert new ones.
    """
    raw_posts = await fetch_external_posts()
    new_count = 0

    for raw in raw_posts:
        source_url = raw.get("url", "")
        if not source_url:
            continue

        existing = db.exec(
            select(Post).where(Post.Source_Url == source_url)
        ).first()
        if existing:
            continue

        post = map_to_post(raw)
        db.add(post)
        new_count += 1

    db.commit()
    return {"ingested": new_count}

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select, func, text, col

from core.database import get_db
from models.post import Post
from models.post_view import PostView
from schemas.post import PostRead

router = APIRouter(prefix="/posts", tags=["posts"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _post_to_read(post: Post) -> PostRead:
    return PostRead(
        id=str(post.id),
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        content=post.content,
        cover_image=post.cover_image,
        tags=post.tags or [],
        category=post.category,
        source_urls=post.source_urls or [],
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------

@router.get("")
def list_posts(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    tag: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(Post).where(func.lower(Post.status) == "published")

    if tag:
        query = query.where(col(Post.tags).any(tag))
    if category:
        query = query.where(Post.category == category)

    # Total count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.exec(count_query).one()

    # Paginated results
    query = query.order_by(Post.created_at.desc())
    query = query.offset((page - 1) * limit).limit(limit)
    posts = db.exec(query).all()

    return {
        "posts": [_post_to_read(p) for p in posts],
        "total": total,
        "page": page,
    }


@router.get("/search")
def search_posts(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    query = select(Post).where(
        func.lower(Post.status) == "published",
        text("post.search_vector @@ plainto_tsquery('english', :q)")
    ).params(q=q)
    posts = db.exec(query).all()
    return {"posts": [_post_to_read(p) for p in posts]}


@router.get("/{slug}")
def get_post_by_slug(slug: str, db: Session = Depends(get_db)):
    post = db.exec(select(Post).where(Post.slug == slug)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _post_to_read(post)


class ViewBody(BaseModel):
    user_agent: Optional[str] = None


@router.post("/{id}/view")
def record_view(id: UUID, body: ViewBody = ViewBody(), db: Session = Depends(get_db)):
    # Verify the post exists
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    view = PostView(post_id=id, user_agent=body.user_agent)
    db.add(view)
    db.commit()
    return {"detail": "View recorded"}

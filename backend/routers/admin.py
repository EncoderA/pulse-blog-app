from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, col, text

from core.database import get_db
from dependencies import require_admin
from models.post import Post
from models.post_view import PostView
from models.user import User
from schemas.post import PostCreate, PostRead, PostUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


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
# CRUD
# ---------------------------------------------------------------------------

@router.get("/posts")
def list_all_posts(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    posts = db.exec(select(Post).order_by(Post.created_at.desc())).all()
    return {
        "posts": [_post_to_read(p) for p in posts],
        "total": len(posts),
    }


@router.post("/posts", response_model=PostRead, status_code=201)
def create_post(
    body: PostCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    # Check slug uniqueness
    existing = db.exec(select(Post).where(Post.slug == body.slug)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    post = Post(
        title=body.title,
        slug=body.slug,
        summary=body.summary,
        content=body.content,
        cover_image=body.cover_image,
        source_urls=body.source_urls,
        tags=body.tags,
        category=body.category,
        status="published",
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return _post_to_read(post)


@router.put("/posts/{id}", response_model=PostRead)
def update_post(
    id: UUID,
    body: PostUpdate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post, key, value)
    post.updated_at = datetime.utcnow()

    db.add(post)
    db.commit()
    db.refresh(post)
    return _post_to_read(post)


@router.delete("/posts/{id}", status_code=204)
def delete_post(
    id: UUID,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Delete associated views first
    views = db.exec(select(PostView).where(PostView.post_id == id)).all()
    for view in views:
        db.delete(view)

    db.delete(post)
    db.commit()


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@router.get("/analytics/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    total_posts = db.exec(select(func.count()).select_from(Post)).one()
    total_views = db.exec(select(func.count()).select_from(PostView)).one()

    # Top post by view count
    top_post_query = (
        select(Post, func.count(PostView.id).label("view_count"))
        .outerjoin(PostView, Post.id == PostView.post_id)
        .group_by(Post.id)
        .order_by(func.count(PostView.id).desc())
        .limit(1)
    )
    top_post_row = db.exec(top_post_query).first()
    top_post = None
    if top_post_row:
        post_obj = top_post_row[0] if isinstance(top_post_row, tuple) else top_post_row
        top_post = _post_to_read(post_obj).model_dump()

    # Top tag by frequency
    top_tag = None
    all_posts = db.exec(select(Post)).all()
    tag_counts: dict[str, int] = {}
    for p in all_posts:
        for t in (p.tags or []):
            tag_counts[t] = tag_counts.get(t, 0) + 1
    if tag_counts:
        top_tag = max(tag_counts, key=tag_counts.get)

    return {
        "total_posts": total_posts,
        "total_views": total_views,
        "top_post": top_post,
        "top_tag": top_tag,
    }


@router.get("/analytics/top-posts")
def analytics_top_posts(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    query = (
        select(Post, func.count(PostView.id).label("view_count"))
        .outerjoin(PostView, Post.id == PostView.post_id)
        .group_by(Post.id)
        .order_by(func.count(PostView.id).desc())
        .limit(limit)
    )
    results = db.exec(query).all()

    posts_with_views = []
    for row in results:
        post_obj = row[0] if isinstance(row, tuple) else row
        view_count = row[1] if isinstance(row, tuple) else 0
        post_data = _post_to_read(post_obj).model_dump()
        post_data["view_count"] = view_count
        posts_with_views.append(post_data)

    return posts_with_views


@router.get("/analytics/traffic")
def analytics_traffic(
    range: str = Query(default="7d", pattern="^(7d|30d)$"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    days = 7 if range == "7d" else 30
    since = datetime.utcnow() - timedelta(days=days)

    query = (
        select(
            func.date(PostView.viewed_at).label("date"),
            func.count(PostView.id).label("views"),
        )
        .where(PostView.viewed_at >= since)
        .group_by(func.date(PostView.viewed_at))
        .order_by(func.date(PostView.viewed_at))
    )
    results = db.exec(query).all()

    return [
        {"date": str(row[0]), "views": row[1]}
        for row in results
    ]


@router.get("/analytics/tags")
def analytics_tags(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    all_posts = db.exec(select(Post)).all()
    tag_counts: dict[str, int] = {}
    for p in all_posts:
        for t in (p.tags or []):
            tag_counts[t] = tag_counts.get(t, 0) + 1

    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"tag": tag, "count": count} for tag, count in sorted_tags]

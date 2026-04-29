from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from core.database import get_db
from dependencies import require_agent
from models.post import Post
from schemas.post import PostCreate, PostRead

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/posts", response_model=PostRead, status_code=201)
def agent_create_post(
    body: PostCreate,
    db: Session = Depends(get_db),
    _agent=Depends(require_agent),
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

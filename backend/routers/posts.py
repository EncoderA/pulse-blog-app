from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlmodel import Session, select, func
from typing import List, Optional
from dependencies import get_db
from models.post import Post
from models.post_view import PostView
from schemas.post import PostSummary, PostRead

router = APIRouter()

@router.get("", response_model=dict)
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    focus_area: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(Post)
    if focus_area:
        query = query.where(Post.Focus_Area == focus_area)
        
    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    
    posts = db.exec(
        query.order_by(Post.Date.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()
    
    return {
        "posts": [PostSummary.model_validate(p) for p in posts],
        "total": total,
        "page": page
    }

@router.get("/search", response_model=dict)
def search_posts(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    query = select(Post).where(
        (Post.Title.ilike(f"%{q}%")) | 
        (Post.Short_Summary.ilike(f"%{q}%"))
    )
    posts = db.exec(query).all()
    
    return {
        "posts": [PostSummary.model_validate(p) for p in posts],
        "total": len(posts)
    }

@router.get("/{id}", response_model=PostRead)
def get_post(
    id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Record view even if post doesn't exist locally
    user_agent = request.headers.get("user-agent")
    view = PostView(post_id=id, user_agent=user_agent)
    db.add(view)
    db.commit()

    post = db.get(Post, id)
    if not post:
        raise HTTPException(404, "Post not found")
        
    # Record view
    user_agent = request.headers.get("user-agent")
    view = PostView(post_id=post.Id, user_agent=user_agent)
    db.add(view)
    db.commit()
    
    return post

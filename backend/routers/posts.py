from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlmodel import Session, select, func
from typing import List, Optional
from dependencies import get_db
from models.post import Post
from models.post_view import PostView
from schemas.post import PostSummary, PostRead
from sqlalchemy import or_, and_
from uuid import UUID

router = APIRouter()

@router.get("", response_model=dict)
def list_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = select(Post)
    if category:
        query = query.where(Post.category == category)
        
    total = db.exec(select(func.count()).select_from(query.subquery())).one()
    
    posts = db.exec(
        query.order_by(Post.created_at.desc())
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
    # Split the search phrase into individual words (e.g. "oil price" -> ["oil", "price"])
    search_words = q.strip().split()
    
    # Create a condition for each word
    word_conditions = []
    for word in search_words:
        word_conditions.append(
            or_(
                Post.title.ilike(f"%{word}%"),
                Post.summary.ilike(f"%{word}%")
            )
        )
        
    # Combine all word conditions with AND 
    # (so the post must contain ALL searched words in any order)
    query = select(Post).where(and_(*word_conditions))
    posts = db.exec(query).all()
    
    return {
        "posts": [PostSummary.model_validate(p) for p in posts],
        "total": len(posts)
    }

@router.get("/{id}", response_model=PostRead)
def get_post(
    id: UUID,
    request: Request,
    db: Session = Depends(get_db)
):
    post = db.get(Post, id)
    if not post:
        raise HTTPException(404, "Post not found")
        
    # Record view
    user_agent = request.headers.get("user-agent")
    view = PostView(post_id=post.id, user_agent=user_agent)
    db.add(view)
    db.commit()
    
    return post

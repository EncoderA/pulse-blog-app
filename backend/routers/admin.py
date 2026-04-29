from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from dependencies import get_db, require_admin
from models.post import Post
from models.post_view import PostView
from services.ingest import ingest_posts

router = APIRouter()

@router.get("/analytics/overview")
def get_analytics_overview(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    total_posts = db.exec(select(func.count(Post.id))).one()
    total_views = db.exec(select(func.count(PostView.id))).one()
    
    # Top post by views
    top_post_query = (
        select(Post.id, Post.title, func.count(PostView.id).label("view_count"))
        .join(PostView, PostView.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .order_by(func.count(PostView.id).desc())
        .limit(1)
    )
    top_post_res = db.exec(top_post_query).first()
    top_post = None
    if top_post_res:
        top_post = {
            "id": str(top_post_res[0]),
            "title": top_post_res[1],
            "view_count": top_post_res[2]
        }
    
    # Top focus area
    from sqlalchemy import text
    top_focus_query = select(text("unnest(focus_areas) as focus_area, count(*) as count"))\
        .select_from(Post.__table__)\
        .group_by(text("focus_area"))\
        .order_by(text("count DESC"))\
        .limit(1)
    
    top_focus_res = db.exec(top_focus_query).first()
    top_focus_area = top_focus_res[0] if top_focus_res else None
    
    return {
        "total_posts": total_posts,
        "total_views": total_views,
        "top_post": top_post,
        "top_focus_area": top_focus_area
    }

@router.get("/analytics/top-posts")
def get_top_posts(
    limit: int = 10,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    query = (
        select(
            Post.id, 
            Post.title, 
            Post.img_url, 
            Post.published_date, 
            func.count(PostView.id).label("view_count")
        )
        .join(PostView, PostView.post_id == Post.id, isouter=True)
        .group_by(Post.id)
        .order_by(func.count(PostView.id).desc())
        .limit(limit)
    )
    results = db.exec(query).all()
    
    return [
        {
            "id": str(r[0]),
            "title": r[1],
            "img_url": r[2],
            "published_date": r[3],
            "view_count": r[4]
        }
        for r in results
    ]

@router.get("/analytics/tags")
def get_analytics_tags(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    from sqlalchemy import text
    query = select(text("unnest(focus_areas) as focus_area, count(*) as count"))\
        .select_from(Post.__table__)\
        .group_by(text("focus_area"))\
        .order_by(text("count DESC"))
    
    results = db.exec(query).all()
    
    return [
        {"focus_area": r[0], "count": r[1]}
        for r in results
    ]

@router.post("/ingest")
async def trigger_ingest(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    result = await ingest_posts(db)
    return result

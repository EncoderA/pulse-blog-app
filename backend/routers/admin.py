import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from dependencies import get_db, require_admin
from models.post import Post
from models.post_view import PostView
from models.web_visitor import WebVisitor
from models.blog_visitor import BlogVisitor
from services.ingest import ingest_posts
from sqlalchemy import cast, String

router = APIRouter()

@router.get("/analytics/overview")
def get_analytics_overview(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    total_posts = db.exec(select(func.count(Post.Id))).one()
    total_views = db.exec(select(func.count(PostView.id))).one()
    
    # Top post by views
    top_post_query = (
        select(Post.Id, Post.Title, func.count(PostView.id).label("view_count"))
        .join(PostView, PostView.post_id == Post.Id, isouter=True)
        .group_by(Post.Id, Post.Title)
        .order_by(func.count(PostView.id).desc())
        .limit(1)
    )
    top_post_res = db.exec(top_post_query).first()
    top_post = None
    if top_post_res:
        top_post = {
            "id": top_post_res[0],
            "title": top_post_res[1],
            "view_count": top_post_res[2]
        }

    # Top focus area
    top_focus_query = select(Post.Focus_Area, func.count(Post.Id).label("count"))\
        .where(Post.Focus_Area != None)\
        .group_by(Post.Focus_Area)\
        .order_by(func.count(Post.Id).desc())\
        .limit(1)

    top_focus_res = db.exec(top_focus_query).first()
    top_focus_area = top_focus_res[0] if top_focus_res else None

    return {
        "total_posts": total_posts,
        "top_post": top_post,
        "top_focus_area": top_focus_area,
    }


@router.get("/analytics/top-posts")
def get_top_posts(
    limit: int = 10,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    query = (
        select(
            Post.Id, 
            Post.Title, 
            Post.Image_Url, 
            Post.Date, 
            func.count(PostView.id).label("view_count")
        )
        .join(PostView, PostView.post_id == Post.Id, isouter=True)
        .group_by(Post.Id, Post.Title, Post.Image_Url, Post.Date)
        .order_by(func.count(PostView.id).desc())
        .limit(limit)
    )
    results = db.exec(query).all()

    return [
        {
            "id": r[0],
            "title": r[1],
            "img_url": r[2][0] if r[2] and len(r[2]) > 0 else None,
            "published_date": r[3],
            "view_count": r[4],
        }
        for r in results
    ]


@router.get("/analytics/tags")
def get_analytics_tags(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    query = select(Post.Focus_Area.label("focus_area"), func.count(Post.Id).label("count"))\
        .where(Post.Focus_Area != None)\
        .group_by(Post.Focus_Area)\
        .order_by(func.count(Post.Id).desc())
    
    results = db.exec(query).all()

    return [
        {"focus_area": r[0], "count": r[1]}
        for r in results if r[0] is not None
    ]


@router.post("/ingest")
async def trigger_ingest(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    result = await ingest_posts(db)
    return result


@router.get("/analytics/web-visits-daily")
def get_web_visits_daily(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    """Return daily web visitor counts, most recent first."""
    query = (
        select(WebVisitor.date, WebVisitor.visitor_count)
        .order_by(WebVisitor.date.desc())
    )
    results = db.exec(query).all()
    return [{"date": r[0], "count": r[1]} for r in results]


@router.get("/analytics/blog-visits-daily")
def get_blog_visits_daily(
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    """Return daily blog visitor counts aggregated across all blog_ids, most recent first."""
    query = (
        select(BlogVisitor.visit_date, func.sum(BlogVisitor.visitor_count).label("count"))
        .group_by(BlogVisitor.visit_date)
        .order_by(BlogVisitor.visit_date.desc())
    )
    results = db.exec(query).all()
    return [{"date": r[0], "count": r[1]} for r in results]


@router.get("/analytics/blog-visits-by-id")
def get_blog_visits_by_id(
    blog_id: str,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_admin)
):
    """Return daily visitor counts for a specific blog_id."""
    query = (
        select(BlogVisitor.visit_date, BlogVisitor.visitor_count)
        .where(BlogVisitor.blog_id == blog_id)
        .order_by(BlogVisitor.visit_date.desc())
    )
    results = db.exec(query).all()
    return [{"date": r[0], "count": r[1]} for r in results]

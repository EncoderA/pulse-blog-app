import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from dependencies import get_db, require_admin
from models.post import Post
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
    total_posts = db.exec(select(func.count(Post.id))).one()

    # Top post by blog visits (all-time)
    top_blog_query = (
        select(BlogVisitor.blog_id, func.sum(BlogVisitor.visitor_count).label("view_count"))
        .group_by(BlogVisitor.blog_id)
        .order_by(func.sum(BlogVisitor.visitor_count).desc())
        .limit(1)
    )
    top_blog_res = db.exec(top_blog_query).first()
    top_post = None
    if top_blog_res:
        top_post = {
            "blog_id": top_blog_res[0],
            "view_count": top_blog_res[1],
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
            Post.id,
            Post.title,
            Post.img_url,
            Post.published_date,
            func.coalesce(func.sum(BlogVisitor.visitor_count), 0).label("view_count"),
        )
        .join(
            BlogVisitor,
            BlogVisitor.blog_id == cast(Post.id, String),
            isouter=True,
        )
        .group_by(Post.id)
        .order_by(func.coalesce(func.sum(BlogVisitor.visitor_count), 0).desc())
        .limit(limit)
    )
    results = db.exec(query).all()

    return [
        {
            "id": str(r[0]),
            "title": r[1],
            "img_url": r[2],
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

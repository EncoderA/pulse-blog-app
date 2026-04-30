import datetime
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from dependencies import get_db
from models.web_visitor import WebVisitor
from models.blog_visitor import BlogVisitor

router = APIRouter()


@router.get("/web-visits-daily")
def get_public_web_visits(db: Session = Depends(get_db)):
    """Public endpoint: daily web visitor counts, most recent first."""
    query = (
        select(WebVisitor.date, WebVisitor.visitor_count)
        .order_by(WebVisitor.date.desc())
    )
    results = db.exec(query).all()
    return [{"date": r[0], "count": r[1]} for r in results]


@router.get("/blog-visits-today")
def get_public_blog_visits_today(db: Session = Depends(get_db)):
    """Public endpoint: blog visitor counts for today, grouped by blog_id."""
    today = datetime.date.today()
    query = (
        select(BlogVisitor.blog_id, BlogVisitor.visitor_count)
        .where(BlogVisitor.visit_date == today)
        .order_by(BlogVisitor.visitor_count.desc())
    )
    results = db.exec(query).all()
    return [{"blog_id": r[0], "count": r[1]} for r in results]


@router.get("/blog-visits-daily")
def get_public_blog_visits_daily(db: Session = Depends(get_db)):
    """Public endpoint: total blog visitor counts per day across all blog_ids."""
    query = (
        select(BlogVisitor.visit_date, func.sum(BlogVisitor.visitor_count).label("count"))
        .group_by(BlogVisitor.visit_date)
        .order_by(BlogVisitor.visit_date.desc())
    )
    results = db.exec(query).all()
    return [{"date": r[0], "count": r[1]} for r in results]

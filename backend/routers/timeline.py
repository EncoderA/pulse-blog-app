from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from dependencies import get_db
from models.timeline_post import TimelinePost
from models.timeline_event import TimelineEvent
from models.timeline_quote import TimelineQuote
from models.timeline_comment import TimelineComment
from schemas.timeline import TimelinePostSummary, TimelinePostDetail, TimelineEventOut, TimelineQuoteOut, TimelineCommentOut

router = APIRouter()


@router.get("/posts", response_model=List[TimelinePostSummary])
def list_timeline_posts(db: Session = Depends(get_db)):
    posts = db.exec(
        select(TimelinePost).order_by(TimelinePost.published_at.desc())
    ).all()
    return posts


@router.get("/posts/{slug}", response_model=TimelinePostDetail)
def get_timeline_post(slug: str, db: Session = Depends(get_db)):
    post = db.exec(
        select(TimelinePost).where(TimelinePost.slug == slug)
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Timeline post not found")

    events = db.exec(
        select(TimelineEvent)
        .where(TimelineEvent.post_id == post.id)
        .order_by(TimelineEvent.sequence_order)
    ).all()

    quotes = db.exec(
        select(TimelineQuote)
        .where(TimelineQuote.post_id == post.id)
        .order_by(TimelineQuote.display_order)
    ).all()

    comments = db.exec(
        select(TimelineComment)
        .where(TimelineComment.post_id == post.id)
        .order_by(TimelineComment.display_order)
    ).all()

    return TimelinePostDetail(
        **TimelinePostSummary.model_validate(post).model_dump(),
        quick_take=post.quick_take,
        background=post.background,
        what_happened=post.what_happened,
        key_highlights=post.key_highlights,
        impact=post.impact,
        whats_next=post.whats_next,
        overview=post.overview,
        impacts_detail=post.impacts_detail,
        source_url=post.source_url,
        events=[TimelineEventOut.model_validate(e) for e in events],
        quotes=[TimelineQuoteOut.model_validate(q) for q in quotes],
        comments=[TimelineCommentOut.model_validate(c) for c in comments],
    )

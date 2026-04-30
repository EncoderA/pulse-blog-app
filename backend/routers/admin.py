import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from dependencies import get_db
from models.timeline_post import TimelinePost
from models.timeline_agent_config import TimelineAgentConfig
from schemas.agent_config import AgentConfigCreate, AgentConfigUpdate, AgentConfigRead

router = APIRouter()


# ── Enrichment status ────────────────────────────────────────────────────────

@router.get("/enrichment/status", response_model=Dict[str, int])
def get_enrichment_status(db: Session = Depends(get_db)):
    """Return count of timeline_posts grouped by ingest_status."""
    rows = db.exec(
        select(TimelinePost.ingest_status, func.count(TimelinePost.id))
        .group_by(TimelinePost.ingest_status)
    ).all()

    counts = {"pending": 0, "enriching": 0, "enriched": 0, "failed": 0}
    for status, count in rows:
        if status in counts:
            counts[status] = count
        else:
            counts[status] = count
    return counts


@router.post("/enrichment/retry-failed", response_model=Dict[str, int])
def retry_failed_posts(db: Session = Depends(get_db)):
    """
    Reset all 'failed' and stale 'enriching' timeline posts back to 'pending'.
    Stale enriching rows are left behind when the backend restarts mid-job.
    """
    stale = db.exec(
        select(TimelinePost).where(
            TimelinePost.ingest_status.in_(["failed", "enriching"])
        )
    ).all()

    for post in stale:
        post.ingest_status = "pending"
        post.retry_count = 0
        db.add(post)

    db.commit()
    return {"reset": len(stale)}


@router.post("/enrichment/run", response_model=Dict[str, str])
async def trigger_enrichment_run():
    """Immediately trigger one enrichment batch (non-blocking background task)."""
    from services.enrichment_service import run_enrichment_batch
    asyncio.create_task(run_enrichment_batch())
    return {"status": "started"}


# ── Agent config CRUD ────────────────────────────────────────────────────────

@router.get("/agent-config", response_model=Optional[AgentConfigRead])
def get_agent_config(db: Session = Depends(get_db)):
    """Return the currently active agent config, or null if none exists."""
    config = db.exec(
        select(TimelineAgentConfig)
        .where(TimelineAgentConfig.active == True)
        .order_by(TimelineAgentConfig.id.desc())
        .limit(1)
    ).first()
    return config


@router.post("/agent-config", response_model=AgentConfigRead)
def create_agent_config(payload: AgentConfigCreate, db: Session = Depends(get_db)):
    """
    Create a new agent config.
    If active=True, deactivates all other configs first (only one active at a time).
    """
    if payload.active:
        existing = db.exec(select(TimelineAgentConfig).where(TimelineAgentConfig.active == True)).all()
        for cfg in existing:
            cfg.active = False
            db.add(cfg)

    now = datetime.now(timezone.utc)
    config = TimelineAgentConfig(
        **payload.model_dump(),
        created_at=now,
        updated_at=now,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


@router.put("/agent-config/{config_id}", response_model=AgentConfigRead)
def update_agent_config(
    config_id: int, payload: AgentConfigUpdate, db: Session = Depends(get_db)
):
    """Update an existing agent config. Setting active=True deactivates all others."""
    config = db.get(TimelineAgentConfig, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="Agent config not found")

    update_data = payload.model_dump(exclude_unset=True)

    if update_data.get("active") is True:
        others = db.exec(
            select(TimelineAgentConfig)
            .where(TimelineAgentConfig.active == True, TimelineAgentConfig.id != config_id)
        ).all()
        for other in others:
            other.active = False
            db.add(other)

    for field, value in update_data.items():
        setattr(config, field, value)
    config.updated_at = datetime.now(timezone.utc)

    db.add(config)
    db.commit()
    db.refresh(config)
    return config

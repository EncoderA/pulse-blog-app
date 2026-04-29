from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from .scheduler import get_scheduler_service
from .service import (
    deprecated_payload,
    get_cleaned_articles,
    semantic_search,
    run_pipeline,
    run_preprocess,
    run_scrape,
)


class RunRequest(BaseModel):
    max_per_source: int = Field(default=10, ge=1, le=100)


@asynccontextmanager
async def lifespan(_: FastAPI):
    scheduler = get_scheduler_service()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.stop()


app = FastAPI(title="Blog KB API", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    scheduler = get_scheduler_service()
    return {
        "status": "ok",
        "scheduler_running": scheduler.running,
        "jobs": scheduler.describe_jobs(),
    }


@app.post("/scrape/run")
def scrape_run(request: RunRequest) -> dict:
    return {"raw": run_scrape(max_per_source=request.max_per_source)}


@app.post("/preprocess/run")
def preprocess_run() -> dict:
    return {"processed": run_preprocess()}


@app.post("/pipeline/run")
def pipeline_run(request: RunRequest) -> dict:
    return run_pipeline(max_per_source=request.max_per_source)



@app.get("/scheduler")
def scheduler_status() -> dict:
    scheduler = get_scheduler_service()
    return {
        "running": scheduler.running,
        "jobs": scheduler.describe_jobs(),
    }


@app.post("/scheduler/trigger")
def scheduler_trigger(request: RunRequest) -> dict:
    scheduler = get_scheduler_service()
    scheduler.max_per_source = request.max_per_source
    scheduler.trigger_once()
    return {
        "status": "triggered",
        "jobs": scheduler.describe_jobs(),
    }


@app.get("/cleaned/articles")
def cleaned_articles(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> dict:
    return get_cleaned_articles(limit=limit, offset=offset)


# @app.get("/status/latest")
# def status_latest() -> dict:
#     return deprecated_payload("/status/latest")


# @app.get("/topics")
# def topics() -> dict:
#     return deprecated_payload("/topics")


# @app.get("/stories")
# def stories() -> dict:
#     return deprecated_payload("/stories")


# @app.get("/timeline")
# def timeline() -> dict:
#     return deprecated_payload("/timeline")
@app.get("/search")
def search(query: str):
    return semantic_search(query)
# Backend Service Overview

## Purpose
`backend` is the core API for the Pulse blog system. It serves blog content, records visits, provides login endpoints, and runs a scheduled ingestion job to pull new posts from an external source.

## Tech Stack
- FastAPI
- SQLModel + SQLAlchemy
- PostgreSQL (via `DATABASE_URL`)
- APScheduler (interval jobs)
- JWT auth via HTTP-only cookie

## Main Responsibilities
- Expose public blog APIs (`/posts`, `/posts/search`, `/posts/{id}`)
- Record page-level analytics:
  - `/analytics/web-visit`
  - `/analytics/blog-visit/{blog_id}`
- Provide authentication endpoints (`/auth/login`, `/auth/me`, `/auth/logout`)
- Run periodic ingestion (`services/ingest.py`) every 3 hours

## Runtime Flow
1. App starts and creates DB tables.
2. Scheduler registers `ingest_job` and starts running every 3 hours.
3. API serves post list/search/detail requests.
4. Reading a post writes an entry in `post_views`.
5. Web/blog visit endpoints increment daily counters.

## Data Model Highlights
- `posts`: canonical blog post records
- `post_views`: row per detail-page view with user-agent
- `web_visitors`: total visits per day
- `blog_visitors`: per-blog, per-day visits

## Current Status Notes
- `routers/admin.py` and `routers/external.py` currently have empty routers.
- Ingestion mapping in `services/ingest.py` is placeholder-oriented and depends on final external API schema.

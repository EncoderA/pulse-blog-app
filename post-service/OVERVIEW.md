# Post-Service App Overview

## Purpose
`post-service` is an ingestion bridge service. It pulls cleaned articles from the knowledge-base database and inserts normalized records into the blog `posts` table.

## Tech Stack
- FastAPI
- SQLAlchemy
- `asyncpg` (for KB source DB reads)
- PostgreSQL/Neon (both KB and post DBs)

## Main Responsibilities
- Read source content from KB database (`cleaned_articles`)
- Transform and normalize article fields
- Deduplicate by `Source_Url`
- Insert into target `posts` table
- Expose ingestion endpoints:
  - `GET /kb-posts` (peek source-side records)
  - `POST /ingest` (copy into post DB)

## Required Environment Variables
- `KB_DB_URL` -> source KB database connection
- `POST_DB_URL` -> target posts database connection

## Runtime Flow
1. Service starts and initializes local model tables.
2. `GET /kb-posts` fetches latest KB records from source DB.
3. `POST /ingest` fetches KB records, validates, checks duplicates, and inserts new posts.
4. Returns ingestion counts (`inserted`, `skipped`).

## Current Status Notes
- Files contain a large amount of historical commented code, indicating iterative development.
- Ingestion writes directly with SQL text statements into `posts` schema matching the main backend model naming.

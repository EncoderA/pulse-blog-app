# Analytics Service Overview

## Purpose
`analytics` is a dedicated analytics microservice focused on scraper/source-level metrics. It computes and serves historical trend data from scraping tables.

## Tech Stack
- FastAPI (backend)
- Async SQLAlchemy
- APScheduler (5-minute refresh interval)
- React + Vite (frontend dashboard)
- Recharts for visualizations

## Main Responsibilities
- Aggregate scraper output into analytics tables:
  - `scraper_analytics` (latest snapshot per source)
  - `scraper_analytics_history` (historical snapshots)
- Provide analytics APIs:
  - `GET /scrapper-analytics/`
  - `POST /scrapper-analytics/refresh`
  - `GET /scrapper-analytics/trend`
  - `GET /scrapper-analytics/comparison`
  - `GET /scrapper-analytics/growth`
- Show a visual dashboard in `analytics/frontend`

## Runtime Flow
1. On backend startup, tables are initialized.
2. Scheduler periodically recomputes source metrics every 5 minutes.
3. Dashboard fetches summary + trend/comparison/growth endpoints.
4. Manual refresh endpoint can trigger immediate recomputation.

## Data Dependencies
- Reads raw scrape tables:
  - `articles`
  - `article_images`
- Writes derived analytics tables:
  - `scraper_analytics`
  - `scraper_analytics_history`

## Current Status Notes
- `backend/main.py` contains duplicate `startup` event definitions; behavior should be validated to ensure intended startup sequence.
- Service uses broad CORS (`allow_origins=["*"]`) at present.

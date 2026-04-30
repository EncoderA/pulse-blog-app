# Pulse Blog App

End-to-end content pipeline and publishing platform with ingestion, API, frontend, and analytics services.

## Documentation Index

- Overall architecture and flow diagrams: `PROJECT_ARCHITECTURE.md`
- Core backend service overview: `backend/OVERVIEW.md`
- Analytics service overview: `analytics/OVERVIEW.md`
- Frontend app overview: `frontend/OVERVIEW.md`
- Post ingestion bridge overview: `post-service/OVERVIEW.md`

## Repository at a Glance

- `backend`: main FastAPI service for posts, auth, and visit analytics
- `frontend`: Next.js web app for news and admin-facing UI
- `analytics`: scraper analytics backend + dashboard frontend
- `post-service`: KB-to-posts ingestion bridge
- `scrap_knowledge2`: scraping/preprocessing pipeline feeding KB tables

## Suggested Reading Order

1. `PROJECT_ARCHITECTURE.md`
2. `backend/OVERVIEW.md`
3. `post-service/OVERVIEW.md`
4. `analytics/OVERVIEW.md`
5. `frontend/OVERVIEW.md`

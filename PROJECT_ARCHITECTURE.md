# Pulse Blog App - Overall Architecture

## What This Project Is About
This repository is a multi-service news/blog platform with a scraping-to-publication pipeline:

- A knowledge/scraping pipeline collects and preprocesses external articles.
- A post-ingestion service moves cleaned content into a blog-ready `posts` schema.
- A core backend serves blog APIs, tracks usage analytics, and supports scheduled ingestion from external APIs.
- A Next.js frontend renders public news pages and admin-oriented UI.
- A separate analytics service computes scraper-source metrics and serves dashboard charts.

In short: **this project is an end-to-end content pipeline + publishing UI + analytics stack for a Pulse-style news/blog product.**

## High-Level Component Diagram

```mermaid
flowchart LR
    A[External News / RSS Sources] --> B[scrap_knowledge2]
    B --> C[(KB Database: cleaned_articles / articles / media)]
    C --> D[post-service]
    D --> E[(Posts Database: posts)]
    E --> F[backend FastAPI]
    F --> G[frontend Next.js]

    C --> H[analytics FastAPI]
    H --> I[analytics dashboard frontend]
```

## Request and Data Flow

```mermaid
sequenceDiagram
    participant U as User Browser
    participant FE as Frontend (Next.js)
    participant BE as Backend API
    participant PDB as Posts DB
    participant AS as Analytics Service
    participant KDB as KB/Scraper DB
    participant PS as Post-Service

    U->>FE: Open /news and article pages
    FE->>BE: Fetch posts (current/target integration path)
    BE->>PDB: Read posts
    PDB-->>BE: Post rows
    BE-->>FE: API response
    FE-->>U: Render content

    U->>BE: Visit tracking endpoints
    BE->>PDB: Update visit counters

    PS->>KDB: Read cleaned_articles
    PS->>PDB: Insert deduplicated posts

    AS->>KDB: Aggregate source/article/image stats
    AS-->>U: Dashboard metrics and trends
```

## Service-by-Service Intent
- `scrap_knowledge2`: scrapes and preprocesses source content into PostgreSQL-first KB tables.
- `post-service`: bridge that maps KB records into blog-ready `posts` rows.
- `backend`: primary app API for posts, auth, and visitor analytics; also schedules ingestion.
- `frontend`: user/admin web interface for browsing and editorial views.
- `analytics`: dedicated scraper analytics backend + charting frontend.

## Current Architectural Observations
- There are signs of active migration from mock/static frontend data to live backend data.
- Some backend routes exist as placeholders (`admin`, `external`) and need implementation if required by UI.
- Multiple services interact with similarly named schemas; a clear environment strategy is important to avoid cross-DB confusion.

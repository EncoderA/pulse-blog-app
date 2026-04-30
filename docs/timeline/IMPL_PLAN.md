# Timeline Feature — End-to-End Implementation Plan

**Goal:** Wire the `/timeline` route off the live `timeline_posts` database instead of static mock data, keeping all existing styling and color schemes intact, and connect the full pipeline: scraper → KB → post-service ingest → `timeline_*` tables → backend API → frontend.

---

## Current State Snapshot

| Layer | Status |
|---|---|
| `/timeline` page (FE) | Exists — renders from `lib/news.ts` **static mock** |
| `/timeline/[id]` page (FE) | Exists — renders from `getNewsItem()` static + `news-detail.ts` static |
| `timeline_posts` / `timeline_events` / `timeline_quotes` / `timeline_comments` / `timeline_images` | **Tables created** (schema applied) — **no data** |
| Backend `/timeline/*` API | **Does not exist** |
| `post-service` ingest | Writes only to `posts` table — **does not touch timeline tables** |
| Scraper KB pipeline | Fully functional → writes `cleaned_articles` + images |

---

## Gap Analysis — Issues to Patch Alongside This Feature

| # | Gap | Severity | Fix Included In |
|---|---|---|---|
| G1 | `PostView` model not imported in `backend/core/database.py` `create_db_and_tables()` — `GET /posts/{id}` crashes on first view insert | **High** | Phase 0 |
| G2 | `timeline/[id]/page.tsx` uses `generateStaticParams()` from static `newsItems` — this will 404 on any real DB ID | **High** | Phase 3 |
| G3 | `news-detail.ts` data (quickTake, keyFacts, topQuotes, articleSections) is fully hardcoded — detail page shows wrong story content for every post | **High** | Phase 3 |
| G4 | `post-service` ingest leaves `Background`, `Highlights`, `Impact`, `Whats_Next`, `Tags`, `Focus_Area` empty — derived fields never populated | **Medium** | Phase 2 |
| G5 | `lib/api.ts` `Post` interface uses `slug`, `tags[]`, `category` — doesn't match actual backend response shape (`Id`, `Focus_Area`, `Image_Url`) | **Medium** | Phase 3 |
| G6 | `BlogVisitor` Alembic migration column name mismatch (`date` vs `visit_date`) — migration 0002 renames a column that doesn't exist as written | **Medium** | Phase 0 |
| G7 | Analytics `main.py` has two identical `@app.on_event("startup")` blocks — two APScheduler instances start | **Low** | Phase 0 (note only) |
| G8 | No deduplication key between `timeline_posts` and `posts` — re-running ingest creates duplicates | **Medium** | Phase 2 |

---

## Phases

---

### Phase 0 — Pre-flight Fixes (No feature code, patch blockers only)

**0.1 — Fix `PostView` table creation**

File: `backend/core/database.py`

`create_db_and_tables()` must import and include `PostView` so the table is created on startup. Currently `GET /posts/{id}` will throw a DB error the first time a view is recorded.

```
# Add this import:
from models.post_view import PostView
# PostView is a SQLModel table=True so create_all picks it up automatically
```

**0.2 — Fix Alembic BlogVisitor migration**

File: `backend/alembic/versions/0002_rename_visit_date.py`

Migration renames `visite_date` → `visit_date` but migration 0001 creates the column as `date`. The rename op should target `date` → `visit_date` instead of `visite_date` → `visit_date`.

**0.3 — Note: Analytics double-startup**

File: `analytics/backend/main.py` — two identical `@app.on_event("startup")` handlers. Second one overwrites the first but still registers two scheduler `add_job` calls. Remove the duplicate block. *(Low priority, does not block timeline feature.)*

---

### Phase 1 — Seed Mock Data in Timeline DB

**Target:** `pulse_blog` database — `timeline_posts`, `timeline_events`, `timeline_quotes`, `timeline_comments` tables.

File to create: `docker/postgres/timeline_seed.sql`

Seed **3 realistic news stories** — Iran–Israel conflict escalation, US tariff war update, and India AI policy (mirrors the UI style in `news.ts`).

#### Story Structure Per Row

Each story inserts:
- 1 row in `timeline_posts` (core metadata + all derived text fields)
- 3–4 rows in `timeline_events` (chronological incidents, matching the "Incident 01 / 02 / 03" pattern already in the UI)
- 2 rows in `timeline_quotes` (notable quoted sentences)
- 2 rows in `timeline_comments` (`is_mock = TRUE`)

#### Story 1 — Iran–Israel Conflict Escalation
```
article_id : 'mock-iran-israel-001'
title      : 'Iran launches retaliatory strikes as regional tensions escalate'
focus_area : '{Middle East, Defence, Geopolitics}'
tags       : '{Iran, Israel, missile strike, regional conflict, US response}'
timeline events:
  - Apr 10 2026 | Iran fires ballistic missiles toward Israeli territory
  - Apr 13 2026 | Iron Dome intercepts; Israel declares emergency session
  - Apr 16 2026 | US deploys carrier group to Eastern Mediterranean
  - Apr 22 2026 | UN Security Council calls emergency vote
```

#### Story 2 — US–China Tariff Escalation
```
article_id : 'mock-us-china-tariff-001'
title      : 'US raises tariffs on Chinese goods to 145%; Beijing retaliates'
focus_area : '{Trade, Economics, US-China Relations}'
tags       : '{tariffs, trade war, supply chain, semiconductors, retaliation}'
timeline events:
  - Apr 02 2026 | White House announces 145% tariff on broad Chinese imports
  - Apr 07 2026 | Beijing responds with 125% counter-tariff on US goods
  - Apr 14 2026 | Markets drop; tech sector warns of supply chain disruption
  - Apr 25 2026 | Both sides agree to back-channel negotiations
```

#### Story 3 — India National AI Policy
```
article_id : 'mock-india-ai-policy-001'
title      : 'India launches national AI policy targeting public infrastructure'
focus_area : '{Technology, Policy, Artificial Intelligence}'
tags       : '{AI policy, India, compute access, digital infrastructure, startups}'
timeline events:
  - Mar 20 2026 | Draft policy circulated to ministries for review
  - Apr 05 2026 | Policy announced with compute access and safety pillars
  - Apr 18 2026 | Implementation committee formed; pilots identified
```

**SQL pattern for each insert:**
```sql
-- timeline_posts
INSERT INTO timeline_posts (article_id, kb_source, title, short_summary, published_at,
  content_length, source_url, tags, is_trending, quick_take,
  background, what_happened, key_highlights, impact, whats_next,
  focus_area, overview, impacts_detail, primary_image_url, ingest_status)
VALUES (...);

-- timeline_events (after post inserted, use RETURNING id or subquery for post_id)
INSERT INTO timeline_events (post_id, event_time, event_title, event_content,
  event_image_url, sequence_order)
SELECT id, '2026-04-10', 'Iran fires ballistic missiles...', '...', null, 1
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

-- timeline_quotes
INSERT INTO timeline_quotes (post_id, quote_text, attributed_to, display_order)
SELECT id, '"We will respond to any aggression with full force."', 'Iranian Foreign Ministry', 1
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';

-- timeline_comments
INSERT INTO timeline_comments (post_id, comment_text, commenter_name,
  commenter_designation, is_mock)
SELECT id, 'This is the most serious escalation in years...', 'Aisha Rahman',
  'Defence Analyst', TRUE
FROM timeline_posts WHERE article_id = 'mock-iran-israel-001';
```

---

### Phase 2 — Backend API for Timeline (`pulse_blog` / `backend` service)

**2.1 — SQLModel models for timeline tables**

Create: `backend/models/timeline_post.py`, `backend/models/timeline_event.py`, `backend/models/timeline_quote.py`, `backend/models/timeline_comment.py`

Mirror the SQL schema exactly. Use `ARRAY(String)` for `tags` and `focus_area`. Add these models to `create_db_and_tables()` imports.

**2.2 — Pydantic response schemas**

Create: `backend/schemas/timeline.py`

```python
class TimelineEventOut(BaseModel):
    id: int
    event_time: datetime | None
    event_title: str | None
    event_content: str | None
    event_image_url: str | None
    sequence_order: int

class TimelineQuoteOut(BaseModel):
    id: int
    quote_text: str
    attributed_to: str | None

class TimelineCommentOut(BaseModel):
    id: int
    comment_text: str
    commenter_name: str | None
    commenter_designation: str | None
    commenter_image_url: str | None

class TimelinePostSummary(BaseModel):
    """Used for the listing page — lightweight"""
    id: int
    article_id: str
    title: str | None
    short_summary: str | None
    published_at: datetime | None
    focus_area: list[str] | None
    tags: list[str] | None
    is_trending: bool
    primary_image_url: str | None
    event_count: int           # derived: count of timeline_events rows

class TimelinePostDetail(TimelinePostSummary):
    """Used for the detail page — full payload"""
    quick_take: str | None
    background: str | None
    what_happened: str | None
    key_highlights: str | None
    impact: str | None
    whats_next: str | None
    overview: str | None
    impacts_detail: str | None
    source_url: str | None
    events: list[TimelineEventOut]
    quotes: list[TimelineQuoteOut]
    comments: list[TimelineCommentOut]
```

**2.3 — Timeline router**

Create: `backend/routers/timeline.py`

```
GET  /timeline/posts              → list[TimelinePostSummary]  (paginated, filterable by focus_area)
GET  /timeline/posts/{id}         → TimelinePostDetail          (full story with events, quotes, comments)
```

Register in `backend/main.py`:
```python
from routers import timeline
app.include_router(timeline.router, prefix="/timeline", tags=["timeline"])
```

**2.4 — Extend post-service ingest to write to timeline tables**

File: `post-service/app/services/ingest_service.py`

After inserting into `posts`, also upsert into `timeline_posts` using `source_url` as the dedup key (G8 fix). Map fields:

| `cleaned_articles` field | → `timeline_posts` column | Transform |
|---|---|---|
| `article_id` | `article_id` | direct |
| `source` | `kb_source` | direct |
| `title` | `title` | direct |
| `summary_raw` (first 2 sentences) | `short_summary` | `summarize(content_raw, 2)` |
| `published_at` | `published_at` | direct |
| `len(content_raw)` | `content_length` | computed |
| `source_url` | `source_url` | direct |
| `extract_keywords() + extract_entities()` | `tags` | NLP (importable from scrap_knowledge2's preprocess helpers or copy locally) |
| `summary_raw` first sentence | `quick_take` | `split_sentences()[0]` |
| `content_raw[:300]` | `background` | placeholder (AI enrichment later) |
| `content_raw[300:600]` | `what_happened` | placeholder |
| `images[0]` | `primary_image_url` | direct |
| `extract_entities()` | `focus_area` | NLP |
| `'enriched'` | `ingest_status` | set on write |

After the main `timeline_posts` row: insert one `timeline_events` row using `published_at` as `event_time` and the full `content_raw` as `event_content`. *(Multi-event splitting via `chunk_text` is a Phase 4 enhancement.)*

---

### Phase 3 — Frontend Wire-up (No style changes)

**3.1 — Add timeline API helper**

File: `frontend/lib/api.ts` — add new types and fetch helpers:

```typescript
export type TimelineEventOut = {
  id: number
  event_time: string | null
  event_title: string | null
  event_content: string | null
  event_image_url: string | null
  sequence_order: number
}

export type TimelineQuoteOut = {
  id: number
  quote_text: string
  attributed_to: string | null
}

export type TimelineCommentOut = {
  id: number
  comment_text: string
  commenter_name: string | null
  commenter_designation: string | null
  commenter_image_url: string | null
}

export type TimelinePostSummary = {
  id: number
  article_id: string
  title: string | null
  short_summary: string | null
  published_at: string | null
  focus_area: string[] | null
  tags: string[] | null
  is_trending: boolean
  primary_image_url: string | null
  event_count: number
}

export type TimelinePostDetail = TimelinePostSummary & {
  quick_take: string | null
  background: string | null
  what_happened: string | null
  key_highlights: string | null
  impact: string | null
  whats_next: string | null
  overview: string | null
  impacts_detail: string | null
  source_url: string | null
  events: TimelineEventOut[]
  quotes: TimelineQuoteOut[]
  comments: TimelineCommentOut[]
}

export async function getTimelinePosts(): Promise<TimelinePostSummary[]> { ... }
export async function getTimelinePost(id: number): Promise<TimelinePostDetail | null> { ... }
```

**3.2 — Update `/timeline` listing page**

File: `frontend/app/timeline/page.tsx`

- Replace `import { newsItems } from "@/lib/news"` with `import { getTimelinePosts } from "@/lib/api"`
- Make the component `async` and call `getTimelinePosts()`
- Map `TimelinePostSummary` → existing Card JSX:
  - `item.id` → numeric (href becomes `/timeline/${item.id}`)
  - `item.focus_area?.[0]` → Badge (was `item.category`)
  - `item.published_at` formatted → "Updated …" span (was `item.date`)
  - `item.title` → CardTitle
  - `item.short_summary` → excerpt paragraph
  - `item.events` (empty for listing) → show `item.event_count` incidents placeholder or fetch events separately

> **No class or color changes.** The existing Card, Badge, CircleDot, ArrowUpRight JSX structure is preserved 1:1.

**3.3 — Update `/timeline/[id]` detail page**

File: `frontend/app/timeline/[id]/page.tsx`

- Remove `generateStaticParams` — switch to fully dynamic (no static export)
- Replace `getNewsItem(id)` with `getTimelinePost(Number(id))`
- Map `TimelinePostDetail` fields to existing JSX sections:

| Static data source | → | Live DB field |
|---|---|---|
| `item.title` | → | `post.title` |
| `item.excerpt` | → | `post.short_summary` |
| `item.date` | → | `post.published_at` (formatted) |
| `item.category` | → | `post.focus_area?.[0]` |
| `sortedTimeline[]` | → | `post.events[]` sorted by `sequence_order` |
| `quickTake[0].description` (What Happened?) | → | `post.what_happened` |
| `quickTake[1].description` (Why It Matters?) | → | `post.impact` |
| `quickTake[2].description` (What's Next?) | → | `post.whats_next` |
| `articleSections` Background | → | `post.background` |
| `articleSections` What Happened? | → | `post.what_happened` |
| `articleSections` Key Highlights | → | `post.key_highlights` (split by newline for bullets) |
| `articleSections` Impact | → | `post.impact` |
| `articleSections` What's Next? | → | `post.whats_next` |
| `keyFacts` Focus Areas | → | `post.focus_area?.join(", ")` |
| `keyFacts` Vision | → | `post.overview` |
| `keyFacts` Implementation | → | `post.impacts_detail` |
| `topQuotes[]` | → | `post.quotes[]` |

> **Icon assignments** for quickTake cards (Sparkles, Lightbulb, Rocket) and keyFacts (CalendarDays, Target, Flag, ClipboardList) are kept as static constants — only the *text content* is swapped from DB.

> **Featured blockquote** at bottom: use `post.quotes[0]` if present, else hide the section.

> **Related Topics** and **You May Also Like**: remain mock / static for now (Phase 5 scope).

---

### Phase 4 — Pipeline Smoke Test (End-to-End Verification)

Run the following sequence manually to verify the full pipeline works:

```
Step 1: Scraper
  POST http://localhost:8002/pipeline/run
  → cleaned_articles populated in pulse_kb

Step 2: Post-service ingest
  POST http://localhost:8001/ingest
  → rows inserted into pulse_blog.posts AND pulse_blog.timeline_posts + timeline_events

Step 3: Backend API
  GET http://localhost:8000/timeline/posts
  → returns list of TimelinePostSummary

  GET http://localhost:8000/timeline/posts/{id}
  → returns TimelinePostDetail with events[]

Step 4: Frontend
  http://localhost:3000/timeline
  → lists live stories from DB (not static mock)

  http://localhost:3000/timeline/{id}
  → shows full story with real timeline events and derived text
```

#### Expected Verification Checklist
- [ ] `/timeline` page shows 3+ stories from DB (Iran war, tariff, AI policy mock seeds)
- [ ] Each story card shows correct event count ("Incident 01, 02, 03...")
- [ ] "Read story" links resolve to `/timeline/{numeric_id}` correctly
- [ ] Detail page shows `what_happened`, `background`, `impact`, `whats_next` from DB
- [ ] Timeline events section renders chronologically by `sequence_order`
- [ ] Top Quotes sidebar shows real quotes from `timeline_quotes` table
- [ ] Color scheme, fonts, spacing unchanged from current design

---

### Phase 5 — Future Enhancements (Out of Scope for This Sprint)

| Enhancement | Description |
|---|---|
| AI enrichment job | APScheduler job that reads `timeline_posts` where `ingest_status = 'pending'`, calls LLM (OpenAI/local) to generate `background`, `what_happened`, `key_highlights`, `impact`, `whats_next` and updates row to `'enriched'` |
| Multi-event chunking | `chunk_text(content_raw)` splits long articles into multiple `timeline_events` rows automatically |
| Related Topics | Tag-based query: `SELECT * FROM timeline_posts WHERE tags && post.tags LIMIT 5` |
| You May Also Like | Same focus_area, different post, ordered by `published_at DESC` |
| Real comments | Remove `is_mock = TRUE` guard and open comment submit endpoint |
| Trending flag | Analytics: set `is_trending = TRUE` on posts with `post_views > threshold` in last 24h |
| `PostView` for timeline | Add `timeline_post_id` FK to `post_views` to track which timeline posts are most read |

---

## File Change Summary

| File | Action | Phase |
|---|---|---|
| `backend/core/database.py` | Import + register `PostView` in `create_db_and_tables` | 0 |
| `backend/alembic/versions/0002_rename_visit_date.py` | Fix column name from `visite_date` to `date` | 0 |
| `docker/postgres/timeline_seed.sql` | Create — 3 mock stories with events, quotes, comments | 1 |
| `backend/models/timeline_post.py` | Create — SQLModel for `timeline_posts` | 2 |
| `backend/models/timeline_event.py` | Create — SQLModel for `timeline_events` | 2 |
| `backend/models/timeline_quote.py` | Create — SQLModel for `timeline_quotes` | 2 |
| `backend/models/timeline_comment.py` | Create — SQLModel for `timeline_comments` | 2 |
| `backend/schemas/timeline.py` | Create — Pydantic response shapes | 2 |
| `backend/routers/timeline.py` | Create — `GET /timeline/posts` + `GET /timeline/posts/{id}` | 2 |
| `backend/main.py` | Register timeline router | 2 |
| `backend/core/database.py` | Add timeline model imports to `create_db_and_tables` | 2 |
| `post-service/app/services/ingest_service.py` | Extend to upsert into `timeline_posts` + `timeline_events` | 2 |
| `frontend/lib/api.ts` | Add `TimelinePost*` types + fetch helpers | 3 |
| `frontend/app/timeline/page.tsx` | Replace static `newsItems` with API call | 3 |
| `frontend/app/timeline/[id]/page.tsx` | Remove `generateStaticParams`, wire API data to existing JSX | 3 |

---

## Design Constraints (Must Be Respected Throughout)

- **No color or class changes** to any existing component in `frontend/app/timeline/`
- The `Badge`, `Card`, `CircleDot`, `ArrowUpRight`, `Separator` usage pattern stays identical
- The existing 7fr / 3fr main + sidebar grid layout on the detail page is preserved
- All new API calls use `cache: "no-store"` to avoid stale data (consistent with `/news` page)
- Backend timeline router uses the same `get_db` session dependency pattern as `routers/posts.py`
- No new npm packages — all types are native TypeScript, all UI uses existing shadcn components

# Timeline Implementation Plan — Gap Review

Reviewed against actual source code on 2026-04-30.
All file paths are relative to `pulse-blog-app/`.

---

## Severity Legend
- 🔴 **Critical** — Will silently fail or cause runtime crashes
- 🟠 **High** — Blocked feature / wrong behaviour, needs a concrete decision before coding
- 🟡 **Medium** — Works but produces wrong output or creates technical debt
- 🟢 **Low** — Polish / future-proof concern

---

## Phase 0 — Pre-flight Fixes

### 🔴 G1-A — `AppVisit` also missing from `create_db_and_tables`

**What the plan says:** Import `PostView` in `backend/core/database.py`.

**What the code shows:** `AppVisit` (in `backend/models/app_visit.py`) is also a `SQLModel, table=True` class with `__tablename__ = "app_visit"` and is **also not imported** in `create_db_and_tables`. Both `PostView` and `AppVisit` need to be added.

```python
# backend/core/database.py — correct fix
import models.post
import models.web_visitor
import models.blog_visitor
import models.post_view    # ← add
import models.app_visit    # ← also add
SQLModel.metadata.create_all(engine)
```

---

### 🟠 G6 — Alembic 0002 fix description is wrong

**What the plan says:** "Fix column name from `visite_date` to `date`."

**What the code actually shows (0001):**
```python
sa.Column('date', sa.Date(), nullable=False),   # column is called 'date'
```
**What 0002 does (wrong):**
```python
op.alter_column('blog_visitor', 'visite_date', new_column_name='visit_date')
# ↑ 'visite_date' does not exist in the table — this throws at migration runtime
```
**Correct fix for 0002:**
```python
op.alter_column('blog_visitor', 'date', new_column_name='visit_date')
# downgrade:
op.alter_column('blog_visitor', 'visit_date', new_column_name='date')
```
The plan description ("fix from `visite_date` to `date`") is backwards — the rename source is `date`, not `visite_date`.

---

## Phase 1 — Seed Mock Data

### 🔴 G-DB — Critical: Backend points to Neon; seed SQL targets Docker Postgres

**What the code shows:**
- `backend/.env` → `DATABASE_URL=postgresql://neondb_owner:...@neon.tech/neondb?sslmode=require`  (Neon cloud DB)
- `docker-compose.full.yml` post-service → `POST_DB_URL: postgresql://postgres:postgres@postgres:5432/pulse_blog`  (local Docker Postgres)
- Timeline schema was applied (user confirmed) — **but to which DB?**

If the `timeline_schema.sql` was run against Neon (via the user's SQL client), the backend API will find the tables.
If it was run against local Docker Postgres, the backend won't see the tables at all.

**Decision needed before Phase 2:**
> Confirm which DB holds `pulse_blog` for the backend — Neon (backend/.env) or local Docker (compose env_file .env). All timeline SQL (schema + seed + ingest writes) must target the same DB.

The two `.env` files currently point to **different databases** for the same logical service. This needs to be reconciled.

---

### 🔴 G-SEED — `timeline_seed.sql` will not auto-run in Docker

**What docker-compose.full.yml mounts:**
```yaml
volumes:
  - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
```
Only `init.sql` is in the init directory. `timeline_schema.sql` and `timeline_seed.sql` will **not execute automatically**.

**Fix options (pick one, add to plan):**
1. Mount both files in `docker-entrypoint-initdb.d/` (Postgres runs all `*.sql` files in alphabetical order):
   ```yaml
   - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/01_init.sql:ro
   - ./docker/postgres/timeline_schema.sql:/docker-entrypoint-initdb.d/02_timeline_schema.sql:ro
   - ./docker/postgres/timeline_seed.sql:/docker-entrypoint-initdb.d/03_timeline_seed.sql:ro
   ```
2. Combine all three files into `init.sql`.
3. Document a manual apply step: `psql -f timeline_seed.sql`.

---

### 🟠 G-EVENTS-LIST — Listing page renders events inline but `TimelinePostSummary` omits `events[]`

**What the current `timeline/page.tsx` does:**
```tsx
const incidents = [...item.timeline].sort(...)   // renders N event cards inside each story card
```
The plan's `TimelinePostSummary` type has `event_count: int` but **no `events[]` array**.

This means the listing page as-written can't be wired up without restructuring the card — either:
- **Option A:** Include `events[]` (lightweight: `event_time` + `event_title` only) in `TimelinePostSummary`. Slightly larger payload but matches current UI exactly.
- **Option B:** Change the listing card to show only a count badge ("3 incidents") instead of rendering each event inline.

The plan must explicitly choose one. Option A is lower-risk (preserves styling).

---

## Phase 2 — Backend API

### 🟠 G-NLP — No concrete plan for NLP helpers in `post-service`

**What the plan says:** "NLP (importable from scrap_knowledge2's preprocess helpers or copy locally)."

**What the code shows:** `post-service` is an independent Python package with its own `Dockerfile` and `requirements.txt`. It has **no dependency** on `scrap_knowledge2`. Importing from `scrap_knowledge2.src.blog_kb.preprocess` will fail with `ModuleNotFoundError`.

**Decision needed:**
- **Copy functions** (`extract_keywords`, `extract_entities`, `summarize`, `split_sentences`) into `post-service/app/utils/nlp.py`. Lightweight — these are pure Python with no heavy dependencies. ✅ Recommended.
- Call the KB API's `/search` endpoint — overkill and couples services.
- Skip NLP in post-service; leave `tags` and `focus_area` empty (populated later by enrichment job).

---

### 🟠 G-MODEL-DRIFT — SQLModel timeline models must exactly match the SQL schema already applied

**What the plan says:** "Create SQLModel models for timeline tables."

**Risk:** The `timeline_schema.sql` was already applied to the database with a specific column order, defaults, and constraints. If the new SQLModel models differ in any way (e.g., default values, nullable flags, column names), `SQLModel.metadata.create_all(engine)` will **silently skip** the existing tables (it only creates, never alters). But runtime ORM operations will fail or return wrong data.

**Recommended addition to plan:**
After writing the SQLModel models, validate each column against `timeline_schema.sql` line by line. Specifically watch:
- `tags TEXT[]` and `focus_area TEXT[]` → must use `sa_column=Column(ARRAY(String))` pattern (same as `Post.Image_Url`)
- `is_trending BOOLEAN DEFAULT FALSE` → `Field(default=False)`
- `ingest_status VARCHAR(50) DEFAULT 'pending'` → `Field(default='pending', max_length=50)`
- `sequence_order SMALLINT NOT NULL DEFAULT 0` → SQLModel maps `SMALLINT` as `SmallInteger` from SQLAlchemy, not the default `Integer`

---

### 🟠 G-EVENT-COUNT — `event_count` has no query implementation described

**What the plan says:** `TimelinePostSummary` includes `event_count: int` ("derived: count of timeline_events rows").

**What's missing:** No SQL/ORM pattern is described for computing this. SQLModel's simple `db.exec(select(TimelinePost))` won't include a count from a related table.

**Concrete implementation needed:**
```python
# Option A: raw SQL with subquery
from sqlalchemy import func, select as sa_select
stmt = (
    sa_select(
        TimelinePost,
        sa_select(func.count(TimelineEvent.id))
        .where(TimelineEvent.post_id == TimelinePost.id)
        .correlate(TimelinePost)
        .scalar_subquery()
        .label("event_count")
    )
)
```
This needs to be specified in the router implementation plan so developers aren't guessing.

---

### 🟠 G-POSTSERVICE-MODELS — `post-service` needs its own SQLAlchemy models for timeline tables

**What the plan says:** Extend `post-service/app/services/ingest_service.py` to write to `timeline_posts` and `timeline_events`.

**What the code shows:** `post-service` has its own `app/db/models.py` with a separate SQLAlchemy `Base`. The main backend's `SQLModel` classes are not accessible from post-service. To write to the timeline tables, post-service needs either:
- New SQLAlchemy models in `post-service/app/db/models.py` (for `timeline_posts` + `timeline_events`)
- Or raw `INSERT` via `sqlalchemy.text(...)` (same pattern already used for `posts` table)

The plan doesn't address this. Raw `text()` inserts are simpler given the existing pattern.

---

### 🟡 G-TIMELINE-ALEMBIC — No Alembic migration for timeline tables

**What the plan says:** Register new SQLModel models in `create_db_and_tables()`.

**Risk:** Timeline tables already exist (created via SQL script). `create_all` skips them. Future schema changes to `timeline_*` tables have no migration path — any column add/rename will require another raw SQL script or a new Alembic migration. The plan should note that Alembic coverage for timeline tables is a Phase 5 task.

---

## Phase 3 — Frontend Wire-up

### 🟠 G-READTIME — `readTime` field unaddressed in detail page

**What `timeline/[id]/page.tsx` renders:**
```tsx
<span className="inline-flex items-center gap-1.5">
  <Clock3 className="size-4 text-primary" />
  {item.readTime}    {/* e.g. "4 min read" */}
</span>
```
**What `TimelinePostDetail` provides:** No `read_time` field.

`content_length` is stored (char count). A simple derivation: `Math.ceil(content_length / 800) + " min read"` (~800 chars/min at average reading speed). Either:
- Add derivation in the frontend: `const readTime = \`${Math.ceil((post.content_length ?? 800) / 800)} min read\``
- Or compute and store in the backend response.

The plan must specify this — without it the `{item.readTime}` render will show `undefined`.

---

### 🟠 G-STATIC-PARAMS — `generateStaticParams` removal may break Next.js build config

**What `timeline/[id]/page.tsx` has:**
```tsx
export function generateStaticParams() {
  return newsItems.map((item) => ({ id: item.id }));
}
```
**Plan says:** Remove it. ✅ Correct.

**Risk to verify:** Check `frontend/next.config.*` for `output: 'export'`. If present, removing `generateStaticParams` from a dynamic route breaks the static export build. Based on reading `layout.tsx` there's no obvious static export but this file wasn't checked. **Add to plan: verify `next.config.ts` before removing `generateStaticParams`.**

---

### 🟡 G-HIGHLIGHTS — `key_highlights` bullet-point format convention not defined

**Current static data:**
```typescript
points: [
  "A national AI compute and data infrastructure program...",
  "Responsible AI guidelines covering transparency...",
]
```
**DB stores:** `key_highlights TEXT` (single string).

The plan says "split by newline for bullets" but the seed data format isn't specified, and the frontend split logic isn't described. Both must match:
- Seed data: store as `"bullet 1\nbullet 2\nbullet 3"`
- Frontend: `post.key_highlights?.split('\n').filter(Boolean)` to get `points[]`
- Backend schema comment should document the `\n`-delimited convention

---

### 🟡 G-URL-FORMAT — Timeline URLs change from slugs to numeric IDs

**Current:** `/timeline/global-markets-open-mixed`
**After Phase 3:** `/timeline/1`, `/timeline/2`, ...

This is a breaking change for any bookmarked or shared URLs. Not a code blocker but should be noted. If SEO or shareable URLs matter, consider adding a `slug` column to `timeline_posts`.

---

### 🟡 G-NULL-FALLBACKS — No null-safety specified for optional DB fields in JSX

**Risk:** If `post.background`, `post.what_happened`, etc. are `null` (as they will be for scraper-ingested rows before AI enrichment), the JSX will render `undefined` or empty sections. The plan doesn't specify null fallback patterns.

**Pattern to add:**
```tsx
{post.background && (
  <div className="space-y-3">
    <h2>Background</h2>
    <p>{post.background}</p>
  </div>
)}
```
Or use a fallback: `{post.background ?? "Content coming soon."}`

---

### 🟡 G-CLIENTSIDE-API-URL — `http://backend:8000` doesn't resolve in browser

**What docker-compose sets:**
```yaml
NEXT_PUBLIC_API_URL: http://backend:8000
```
**Risk:** `NEXT_PUBLIC_*` variables are inlined at build time and also available on the client. Inside Docker containers, `backend:8000` resolves (Docker DNS). But in the user's browser, `backend` is not a valid hostname — API calls from client components will fail.

Server components (async page functions) make the fetch server-side, so they work fine inside Docker. But any future client-side fetching (e.g., pagination, filters) will break.

**Not introduced by timeline feature**, but Phase 3 adds more `fetch` calls. Recommend documenting that all timeline fetches stay in server components.

---

## Summary Table

| # | Gap | Phase | Severity | Action |
|---|---|---|---|---|
| G1-A | `AppVisit` also missing from `create_db_and_tables` | 0 | 🔴 | Add import alongside `PostView` |
| G6 | Alembic 0002 fix description is backwards | 0 | 🟠 | Change source column from `visite_date` → `date` |
| G-DB | Backend (Neon) vs post-service (Docker postgres) DB mismatch | 1 | 🔴 | Decide and align on one `pulse_blog` target |
| G-SEED | `timeline_seed.sql` won't auto-run in Docker | 1 | 🔴 | Mount in compose or document manual apply |
| G-EVENTS-LIST | Listing page needs events inline; summary type omits them | 1/3 | 🟠 | Add lightweight `events[]` to summary response |
| G-NLP | NLP helpers unavailable in post-service container | 2 | 🟠 | Copy 4 functions to `post-service/app/utils/nlp.py` |
| G-MODEL-DRIFT | SQLModel models must exactly match applied SQL schema | 2 | 🟠 | Validate column by column; document ARRAY pattern |
| G-EVENT-COUNT | No query implementation for `event_count` derived field | 2 | 🟠 | Add correlated subquery pattern to router plan |
| G-POSTSERVICE-MODELS | post-service needs models/raw SQL for timeline tables | 2 | 🟠 | Use `text()` INSERT pattern (matches existing style) |
| G-TIMELINE-ALEMBIC | No Alembic migration for timeline tables | 2 | 🟡 | Note as Phase 5 task |
| G-READTIME | `readTime` renders `undefined` after static data removed | 3 | 🟠 | Derive from `content_length` in FE or backend |
| G-STATIC-PARAMS | `generateStaticParams` removal may break export build | 3 | 🟠 | Check `next.config.ts` first |
| G-HIGHLIGHTS | `key_highlights` bullet format convention undefined | 3 | 🟡 | Define `\n`-delimited in seed + FE split |
| G-URL-FORMAT | Slug URLs break, numeric IDs take over | 3 | 🟡 | Note / add `slug` column if SEO needed |
| G-NULL-FALLBACKS | Null DB fields render as `undefined` in JSX | 3 | 🟡 | Add `?? ""` or conditional rendering pattern |
| G-CLIENTSIDE | `backend:8000` unresolvable from browser | 3 | 🟡 | Keep all timeline fetches in server components |

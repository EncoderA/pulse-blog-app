-- =============================================================================
-- TIMELINE FEATURE SCHEMA
-- Target database : pulse_blog
-- =============================================================================
--
-- FIELD MAPPING  (KB pipeline → Timeline UI)
-- ─────────────────────────────────────────────────────────────────────────────
-- Scrapper pipeline produces two tiers of tables inside pulse_kb:
--
--   RAW tier   : articles, article_images, article_videos
--   CLEAN tier : cleaned_articles, cleaned_article_images, cleaned_article_videos
--
-- Columns available in cleaned_articles after preprocess.py runs:
--   article_id     VARCHAR(100)   – MD5 hash of source URL (primary key)
--   source         TEXT           – news source name  (e.g. "Reuters")
--   source_url     TEXT           – original article URL
--   title          TEXT           – normalised headline
--   summary_raw    TEXT           – 4-sentence NLP summary of content_raw
--   published_at   TIMESTAMPTZ    – parsed publish date
--   content_raw    TEXT           – full cleaned article text
--   file_content   TEXT           – "title | summary | keywords: … | entities: …"
--   status         VARCHAR(50)    – "processed"
--
-- cleaned_article_images(article_id, image_url)
-- cleaned_article_videos(article_id, video_url)
--
-- NLP helpers available via preprocess.py (called during ingest):
--   summarize(content_raw, 2)         → short_summary  (2 sentences)
--   summarize(content_raw, 4)         → summary_raw stored in cleaned_articles
--   split_sentences(summary_raw)[0]   → quick_take
--   extract_keywords(content_raw)     → tags[]
--   extract_entities(content_raw)     → focus_area[]
--   chunk_text(content_raw)           → timeline event content blocks
--   char_length(content_raw)          → content_length
--   AI LLM call on content_raw        → background, what_happened, key_highlights,
--                                        impact, whats_next, overview, impacts, quotes
--
-- ─────────────────────────────────────────────────────────────────────────────
-- COMPLETE FIELD MAPPING TABLE
-- ─────────────────────────────────────────────────────────────────────────────
-- Sec  UI Field               Type      KB Source Table          KB Column(s)          Derivation Method                          Timeline Table.Column
-- ───  ────────────────────   ───────   ─────────────────────    ──────────────────    ────────────────────────────────────────   ──────────────────────────────
-- 1    Title                  Direct    cleaned_articles         title                 1:1 copy                                   timeline_posts.title
-- 1    Short Summary          Derived   cleaned_articles         content_raw           summarize(content_raw, 2)                  timeline_posts.short_summary
--
-- 2    Date                   Direct    cleaned_articles         published_at          1:1 copy                                   timeline_posts.published_at
-- 2    Content Length         Derived   cleaned_articles         content_raw           char_length(content_raw)                   timeline_posts.content_length
-- 2    AI Policy              NA        —                        —                     Always FALSE (spec: No)                    timeline_posts.is_ai_policy
-- 2    Tags                   Derived   cleaned_articles         content_raw           extract_keywords() + extract_entities()    timeline_posts.tags  TEXT[]
-- 2    Trending               Mock      —                        —                     Default FALSE, overridable                 timeline_posts.is_trending
-- 2    Source URL             Direct    cleaned_articles         source_url            1:1 copy                                   timeline_posts.source_url
--
-- 3    QuickTake              Derived   cleaned_articles         summary_raw           split_sentences(summary_raw)[0]            timeline_posts.quick_take
--
-- 4    Story Timeline: time   Direct    cleaned_articles         published_at          1:1 copy per event row                     timeline_events.event_time
-- 4    Story Timeline: title  Direct    cleaned_articles         title                 1:1 copy (or AI-split heading per event)   timeline_events.event_title
-- 4    Story Timeline: content Direct   cleaned_articles         content_raw           chunk_text(content_raw) per event slot     timeline_events.event_content
-- 4    Story Timeline: image  Direct    cleaned_article_images   image_url             One image mapped per event by order        timeline_events.event_image_url
--
-- 5    Background             Derived   cleaned_articles         content_raw           AI: contextual background of the story     timeline_posts.background
-- 5    What Happened          Derived   cleaned_articles         content_raw           AI: core event description  (≈ posts.News) timeline_posts.what_happened
-- 5    Key Highlights         Derived   cleaned_articles         content_raw           AI: bullet highlights (≈ posts.Highlights) timeline_posts.key_highlights
-- 5    Impact                 Derived   cleaned_articles         content_raw           AI: impact statement  (≈ posts.Impact)     timeline_posts.impact
-- 5    What's Next            Derived   cleaned_articles         content_raw           AI: future implications (≈ posts.Whats_Next) timeline_posts.whats_next
--
-- 6    Comment                Mock      —                        —                     Mock until community feature ships         timeline_comments.comment_text
-- 6    Name                   Mock      —                        —                     Mock                                       timeline_comments.commenter_name
-- 6    Designation            Mock      —                        —                     Mock                                       timeline_comments.commenter_designation
-- 6    Image                  Mock      —                        —                     Mock                                       timeline_comments.commenter_image_url
--
-- 7    What Do You Think      NA        —                        —                     Poll widget, no DB storage needed          (no table — UI only)
--
-- 8    Policy Announced       NA        —                        —                     Always FALSE (spec: No)                    timeline_posts.policy_announced
-- 8    Focus Area (tags)      Derived   cleaned_articles         content_raw           extract_entities() (≈ posts.Focus_Area)   timeline_posts.focus_area  TEXT[]
-- 8    Overview (Vision)      Derived   cleaned_articles         content_raw           AI: high-level narrative (≈ posts.Overview) timeline_posts.overview
-- 8    Impacts (Implementations) Derived cleaned_articles        content_raw           AI: implementation details (≈ posts.Impacts) timeline_posts.impacts_detail
-- 8    Top Quotes             Derived   cleaned_articles         content_raw           AI/regex: extract notable quoted sentences  timeline_quotes.quote_text
-- 8    Related Topics         Mock      —                        —                     Mock until Dashboard team feeds data       (no table — UI mock)
-- 8    You May Also Like      Mock      —                        —                     Mock / future recommendation engine        (no table — UI mock)
--
-- 9    Image URL              Direct    cleaned_article_images   image_url             All images; [0] becomes primary            timeline_images.image_url
-- =============================================================================


-- =============================================================================
-- TABLE DEFINITIONS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- 1. timeline_posts
--    One row per scraped article promoted into the Timeline feature.
--    Covers UI Sections 1, 2, 3, 5, 8 and the primary image from Section 9.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS timeline_posts (
    -- Identity & KB linkage
    id                  SERIAL          PRIMARY KEY,
    article_id          VARCHAR(100)    NOT NULL UNIQUE,    -- cleaned_articles.article_id
    kb_source           TEXT,                               -- cleaned_articles.source  (e.g. "Reuters")
    slug                VARCHAR(255)    UNIQUE,             -- URL-safe slug derived from title (e.g. "iran-launches-retaliatory-strikes")

    -- ── Section 1 : Post ────────────────────────────────────────────────────
    title               TEXT,                               -- Direct  ← cleaned_articles.title
    short_summary       TEXT,                               -- Derived ← summarize(content_raw, 2)

    -- ── Section 2 : Post Metadata ───────────────────────────────────────────
    published_at        TIMESTAMPTZ,                        -- Direct  ← cleaned_articles.published_at
    content_length      INTEGER,                            -- Derived ← char_length(content_raw)
    source_url          TEXT,                               -- Direct  ← cleaned_articles.source_url
    tags                TEXT[],                             -- Derived ← extract_keywords() + extract_entities()
    is_trending         BOOLEAN         DEFAULT FALSE,      -- Mock    (overridable flag)
    is_ai_policy        BOOLEAN         DEFAULT FALSE,      -- NA      (spec: always No)

    -- ── Section 3 : Post Conversation / QuickTake ───────────────────────────
    quick_take          TEXT,                               -- Derived ← split_sentences(summary_raw)[0]

    -- ── Section 5 : Detailed Summary ────────────────────────────────────────
    background          TEXT,                               -- Derived ← AI extract from content_raw  (≈ posts.Background)
    what_happened       TEXT,                               -- Derived ← AI extract from content_raw  (≈ posts.News)
    key_highlights      TEXT,                               -- Derived ← AI extract from content_raw  (≈ posts.Highlights)
    impact              TEXT,                               -- Derived ← AI extract from content_raw  (≈ posts.Impact)
    whats_next          TEXT,                               -- Derived ← AI extract from content_raw  (≈ posts.Whats_Next)

    -- ── Section 8 : Key Facts ───────────────────────────────────────────────
    policy_announced    BOOLEAN         DEFAULT FALSE,      -- NA      (spec: always No)
    focus_area          TEXT[],                             -- Derived ← extract_entities()           (≈ posts.Focus_Area)
    overview            TEXT,                               -- Derived ← AI high-level narrative      (≈ posts.Overview, was "Vision")
    impacts_detail      TEXT,                               -- Derived ← AI implementation details    (≈ posts.Impacts, was "Implementations")

    -- ── Section 9 : Primary Image ───────────────────────────────────────────
    primary_image_url   TEXT,                               -- Direct  ← cleaned_article_images.image_url [0]

    -- ── Audit ───────────────────────────────────────────────────────────────
    ingest_status       VARCHAR(50)     DEFAULT 'pending',  -- pending | enriched | published
    created_at          TIMESTAMPTZ     DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     DEFAULT NOW()
);

COMMENT ON TABLE  timeline_posts IS 'Core enriched post record for the Timeline feature. One row per article from the KB pipeline.';
COMMENT ON COLUMN timeline_posts.article_id         IS 'FK link to pulse_kb.cleaned_articles.article_id (cross-DB reference, not enforced by FK constraint).';
COMMENT ON COLUMN timeline_posts.tags               IS 'Section 2 – Derived: extract_keywords(content_raw) + extract_entities(content_raw).';
COMMENT ON COLUMN timeline_posts.quick_take         IS 'Section 3 – Derived: first sentence of cleaned_articles.summary_raw.';
COMMENT ON COLUMN timeline_posts.focus_area         IS 'Section 8 – Derived: named entities extracted from content_raw (maps to posts.Focus_Area).';
COMMENT ON COLUMN timeline_posts.overview           IS 'Section 8 – Renamed from "Vision". AI-derived high-level narrative (maps to posts.Overview).';
COMMENT ON COLUMN timeline_posts.impacts_detail     IS 'Section 8 – Renamed from "Implementations". AI-derived impact details (maps to posts.Impacts).';


-- ---------------------------------------------------------------------------
-- 2. timeline_images
--    All images for a post (Section 9).
--    Direct ← cleaned_article_images.image_url   (one row per image URL)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS timeline_images (
    id              SERIAL          PRIMARY KEY,
    post_id         INTEGER         NOT NULL REFERENCES timeline_posts(id) ON DELETE CASCADE,
    image_url       TEXT            NOT NULL,       -- Direct ← cleaned_article_images.image_url
    is_primary      BOOLEAN         DEFAULT FALSE,  -- TRUE for the first / featured image
    display_order   SMALLINT        DEFAULT 0       -- ascending = render order
);

COMMENT ON TABLE timeline_images IS 'Section 9: All image URLs associated with a timeline post (1-to-many).';


-- ---------------------------------------------------------------------------
-- 3. timeline_events
--    Story Timeline entries (Section 4).
--    A single article may be broken into multiple chronological events using
--    chunk_text(content_raw) or AI sentence-level extraction.
--    For articles that map to a single event, insert one row.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS timeline_events (
    id              SERIAL          PRIMARY KEY,
    post_id         INTEGER         NOT NULL REFERENCES timeline_posts(id) ON DELETE CASCADE,

    -- Section 4 fields
    event_time      TIMESTAMPTZ,                    -- Direct  ← cleaned_articles.published_at (or AI-extracted datetime within content)
    event_title     TEXT,                           -- Direct  ← cleaned_articles.title         (or AI-extracted event heading)
    event_content   TEXT,                           -- Direct  ← chunk_text(content_raw) slice  (one chunk per event row)
    event_image_url TEXT,                           -- Direct  ← cleaned_article_images.image_url matched by display_order

    sequence_order  SMALLINT        NOT NULL DEFAULT 0  -- ascending order within the story timeline
);

COMMENT ON TABLE timeline_events IS 'Section 4: Chronological story timeline entries. Each row is one event/chapter within a post.';
COMMENT ON COLUMN timeline_events.event_content IS 'Derived via chunk_text(content_raw) for multi-event stories; full content_raw for single-event articles.';


-- ---------------------------------------------------------------------------
-- 4. timeline_quotes
--    Top Quotes (Section 8 – "keep random quotes").
--    Derived ← AI or regex extraction of notable quoted sentences from content_raw.
--    Multiple quotes per post, rendered randomly or by display_order.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS timeline_quotes (
    id              SERIAL          PRIMARY KEY,
    post_id         INTEGER         NOT NULL REFERENCES timeline_posts(id) ON DELETE CASCADE,

    quote_text      TEXT            NOT NULL,       -- Derived ← AI/regex extract from content_raw
    attributed_to   TEXT,                           -- Derived ← entity closest to quote (optional)
    display_order   SMALLINT        DEFAULT 0
);

COMMENT ON TABLE timeline_quotes IS 'Section 8 Top Quotes: AI/pattern-extracted notable quotes from article content.';


-- ---------------------------------------------------------------------------
-- 5. timeline_comments
--    Popular Comments (Section 6). All MOCK until a real community feature ships.
--    is_mock flag allows the ingest service to distinguish real vs. seeded rows.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS timeline_comments (
    id                      SERIAL          PRIMARY KEY,
    post_id                 INTEGER         NOT NULL REFERENCES timeline_posts(id) ON DELETE CASCADE,

    comment_text            TEXT            NOT NULL,   -- Mock
    commenter_name          VARCHAR(150),               -- Mock
    commenter_designation   VARCHAR(150),               -- Mock
    commenter_image_url     TEXT,                       -- Mock

    is_mock                 BOOLEAN         DEFAULT TRUE,
    display_order           SMALLINT        DEFAULT 0,
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

COMMENT ON TABLE timeline_comments IS 'Section 6 Popular Comments: mock data until a real community comment feature is built.';


-- =============================================================================
-- INDEXES
-- =============================================================================

-- timeline_posts
CREATE INDEX IF NOT EXISTS idx_tlp_article_id     ON timeline_posts(article_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_tlp_slug    ON timeline_posts(slug);
CREATE INDEX IF NOT EXISTS idx_tlp_published_at   ON timeline_posts(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_tlp_ingest_status  ON timeline_posts(ingest_status);
CREATE INDEX IF NOT EXISTS idx_tlp_tags           ON timeline_posts USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_tlp_focus_area     ON timeline_posts USING GIN(focus_area);

-- child tables
CREATE INDEX IF NOT EXISTS idx_tli_post_id        ON timeline_images(post_id);
CREATE INDEX IF NOT EXISTS idx_tle_post_id        ON timeline_events(post_id, sequence_order);
CREATE INDEX IF NOT EXISTS idx_tlq_post_id        ON timeline_quotes(post_id);
CREATE INDEX IF NOT EXISTS idx_tlc_post_id        ON timeline_comments(post_id);


-- =============================================================================
-- AUTO-UPDATE updated_at TRIGGER
-- =============================================================================

CREATE OR REPLACE FUNCTION fn_set_timeline_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_timeline_posts_updated_at
    BEFORE UPDATE ON timeline_posts
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_timeline_updated_at();


-- =============================================================================
-- MIGRATION: Add slug column to an existing timeline_posts table
-- Run this in the Neon SQL console if the table was created before slug was added
-- =============================================================================
-- ALTER TABLE timeline_posts ADD COLUMN IF NOT EXISTS slug VARCHAR(255) UNIQUE;
-- CREATE UNIQUE INDEX IF NOT EXISTS idx_tlp_slug ON timeline_posts(slug);

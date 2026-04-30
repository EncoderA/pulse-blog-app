# pgvector Verification Checklist

Run these queries against your `pgvector-docker` Postgres instance to validate the embedding + similarity dedupe flow.

## 1) Verify pgvector extension is installed

```sql
SELECT extname
FROM pg_extension
WHERE extname = 'vector';
```

Expected: exactly 1 row with `vector`.

## 2) Verify embedding table exists

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('article_embeddings');
```

Expected: `article_embeddings`.

## 3) Verify schema of the embeddings column

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'article_embeddings'
  AND column_name IN ('embedding', 'article_id');
```

Expected:
- `article_id` exists
- `embedding` is a pgvector `vector` type when `pgvector` python package is installed (otherwise it may appear as `text` in `information_schema`, but the pipeline should still behave correctly on Postgres).

## 4) Verify similarity-threshold skip behavior

Before running a scrape, capture baseline counts:

```sql
SELECT (SELECT COUNT(*) FROM articles) AS articles_count,
       (SELECT COUNT(*) FROM cleaned_articles) AS cleaned_articles_count,
       (SELECT COUNT(*) FROM article_embeddings) AS embeddings_count;
```

Then:
1) Set a very high threshold (so more candidates are skipped), for example `SIMILARITY_THRESHOLD=0.99`.
2) Trigger a scrape+pipeline run (whatever you normally do).
3) Re-run the baseline query.

Expected:
- If no new articles are accepted, `articles_count` and `embeddings_count` should not increase.
- `cleaned_articles_count` should not increase either (because preprocessing only upserts cleaned rows for articles that actually exist).

Now repeat with a very low threshold (so more candidates are accepted), for example `SIMILARITY_THRESHOLD=0.0`:

Expected:
- `articles_count`, `embeddings_count`, and `cleaned_articles_count` should increase after the run (unless your RSS feeds produce only previously seen `content_hash` values).

## 5) Verify UTC storage in cleaned articles

This project stores cleaned `published_at` as UTC-native timestamps (no tzinfo on the Python side).

```sql
SELECT published_at
FROM cleaned_articles
WHERE published_at IS NOT NULL
ORDER BY published_at DESC
LIMIT 5;
```

Expected:
- Values should be consistent UTC timestamps (typically ending up as UTC times when you compare to source timestamps).


# Blog KB Pipeline

This project builds a PostgreSQL-first scraping and preprocessing pipeline.

## What it does

- Scrapes a curated set of RSS/news sources.
- Stores raw content in PostgreSQL tables: `articles`, `article_images`, `article_videos`.
- Runs basic normalization/cleaning from PostgreSQL records and updates those same rows.
- Exposes a FastAPI service with a simple built-in scheduler.

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
set DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME
blog-kb run --max-per-source 10
```

Run the API:

```bash
blog-kb serve --host 127.0.0.1 --port 8000
```

Useful endpoints:

- `GET /health`
- `POST /scrape/run`
- `POST /preprocess/run`
- `POST /pipeline/run`
- `GET /status/latest`
- `GET /topics`
- `GET /stories`
- `GET /timeline`
- `GET /scheduler`
- `POST /scheduler/trigger`

## Docker (app + database)

This runs **both the API and PostgreSQL (with pgvector)** inside Docker. The app connects to the database via the Compose service name (`db`) so it does **not** reference any local database.

```bash
docker compose up --build
```

Then open:

- `http://127.0.0.1:8000/health`

### Embeddings / `sentence-transformers` (optional)

By default the Docker image builds **without** the embeddings stack to avoid pulling a very large GPU/CUDA PyTorch distribution.

To enable embeddings locally (non-Docker):

```bash
pip install -e ".[embeddings]"
```

If you need embeddings features, rebuild with:

```bash
docker compose build --build-arg INSTALL_EMBEDDINGS=1 app
docker compose up -d
```

To run a one-off pipeline execution inside the container:

```bash
docker compose run --rm app blog-kb run --max-per-source 10
```

## Database schema

- `articles(article_id PK, source, source_category, url UNIQUE, title, summary_raw, scraped_at, published_at_raw, content_raw, content_hash, status, file_content)`
- `article_images(id PK, article_id FK, image_url)`
- `article_videos(id PK, article_id FK, video_url)`

## Notes

- URL uniqueness is enforced via a DB-level unique constraint on `articles.url`.
- The scraper upserts by URL and refreshes media rows on each run.
- Clustering/topic-rules/indexes/blog-cache/state file generation have been removed.
- Temporary compatibility endpoints (`/status/latest`, `/topics`, `/stories`, `/timeline`) return deprecation payloads.

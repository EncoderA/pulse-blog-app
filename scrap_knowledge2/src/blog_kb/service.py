from __future__ import annotations

from threading import Lock
from typing import Any

from sqlalchemy import select, text

from .db import CleanedArticle, init_db, session_scope
from .preprocess import preprocess_latest_raw
from .scraper import persist_raw, scrape_sources
from .storage import iso_now

_RUN_LOCK = Lock()


def deprecated_payload(endpoint: str) -> dict[str, Any]:
    return {
        "deprecated": True,
        "endpoint": endpoint,
        "message": "This endpoint is no longer supported in PostgreSQL-first simplified mode.",
        "updated_at": iso_now(),
    }


def run_scrape(max_per_source: int = 10) -> dict[str, Any]:
    with _RUN_LOCK:
        init_db()
        records = scrape_sources(max_per_source=max_per_source)
        result = persist_raw(records)
        result["mode"] = "postgresql"
        return result


def run_preprocess() -> dict[str, Any]:
    with _RUN_LOCK:
        init_db()
        result = preprocess_latest_raw()
        result["mode"] = "postgresql"
        return result


def run_pipeline(max_per_source: int = 10) -> dict[str, Any]:
    with _RUN_LOCK:
        init_db()
        raw_result = persist_raw(scrape_sources(max_per_source=max_per_source))
        processed_result = preprocess_latest_raw()
        return {"raw": raw_result, "processed": processed_result, "mode": "postgresql"}


from .db import CleanedArticle, ArticleEmbedding


def get_cleaned_articles(limit: int = 50, offset: int = 0) -> dict[str, Any]:
    init_db()

    with session_scope() as session:
        rows = (
            session.execute(
                select(CleanedArticle, ArticleEmbedding.embedding)
                .outerjoin(
                    ArticleEmbedding,
                    CleanedArticle.article_id == ArticleEmbedding.article_id
                )
                .order_by(CleanedArticle.id.desc())
                .offset(offset)
                .limit(limit)
            )
        ).all()

        records = []

        for article, embedding in rows:
            records.append(
                {
                    "article_id": article.article_id,
                    "source": article.source,
                    "source_url": article.source_url,
                    "title": article.title,
                    "summary_raw": article.summary_raw,
                    "published_at": article.published_at.isoformat() if article.published_at else None,
                    "content_raw": article.content_raw,
                    "status": article.status,
                    "file_content": article.file_content,

                    # relations
                    "images": [img.image_url for img in article.images],
                    "videos": [vid.video_url for vid in article.videos],

                    # ⚠️ optional (avoid in production)
                    "embedding": embedding.tolist() if embedding is not None else None,
                }
            )

        return {
            "count": len(records),
            "limit": limit,
            "offset": offset,
            "items": records,
        }


_MODEL_LOCK = Lock()
_MODEL: Any | None = None


def _get_sentence_transformer_model() -> Any:
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "Embeddings/search requires optional dependencies. "
                'Install with: pip install -e ".[embeddings]" '
                "or build the Docker image with INSTALL_EMBEDDINGS=1."
            ) from e

        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        return _MODEL


def semantic_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    model = _get_sentence_transformer_model()
    query_embedding = model.encode(query).tolist()

    with session_scope() as session:
        results = session.execute(
            text(
                """
            SELECT 
                ca.article_id,
                ca.title,
                ca.summary_raw,
                ca.published_at,
                1 - (ae.embedding <=> :query_embedding) AS similarity
            FROM article_embeddings ae
            JOIN cleaned_articles ca 
                ON ae.article_id = ca.article_id
            ORDER BY ae.embedding <=> :query_embedding
            LIMIT :limit
            """
            ),
            {"query_embedding": query_embedding, "limit": limit}
        ).fetchall()

    return [
        {
            "article_id": r[0],
            "title": r[1],
            "summary": r[2],
            "published_at": r[3],
            "similarity": float(r[4]),
        }
        for r in results
    ]
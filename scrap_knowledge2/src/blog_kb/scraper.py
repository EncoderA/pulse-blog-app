from __future__ import annotations

import hashlib
import os
import re
from datetime import datetime, timezone
from collections.abc import Iterable
from typing import Any

import feedparser
import requests
import trafilatura
from bs4 import BeautifulSoup
from sqlalchemy import select, text

from .config import SOURCES
from .db import Article, ArticleEmbedding, PGVECTOR_AVAILABLE, init_db, session_scope, upsert_article
from .storage import iso_now
from .embeddings import EMBEDDING_DIM as MODEL_EMBEDDING_DIM, embed_text

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BlogKBAgent/0.1)"}


def stable_id(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()


def clean_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.text


def extract_article(url: str) -> dict[str, Any]:
    html = ""
    text = ""
    images: list[str] = []
    videos: list[str] = []

    try:
        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src")
            if src and src.startswith("http"):
                images.append(src)
        for node in soup.find_all(["video", "iframe"]):
            src = node.get("src")
            if src:
                videos.append(src)
    except requests.RequestException:
        html = ""

    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False) or ""
    except Exception:
        text = text or ""

    if not text and html:
        soup = BeautifulSoup(html, "html.parser")
        text = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))

    return {
        "content_raw": clean_space(text),
        "images": list(dict.fromkeys(images))[:20],
        "videos": list(dict.fromkeys(videos))[:10],
    }


def build_raw_record(source: dict[str, str], entry: Any) -> dict[str, Any]:
    url = entry.get("link", "").strip()
    title = clean_space(entry.get("title", ""))
    summary = clean_space(entry.get("summary", "") or entry.get("description", ""))
    article = extract_article(url)
    return {
        "article_id": stable_id(url),
        "source": source["name"],
        "source_category": source["category"],
        "url": url,
        "title": title,
        "summary_raw": summary,
        "scraped_at": iso_now(),
        "published_at_raw": str(entry.get("published", "") or entry.get("updated", "")),
        "content_raw": article["content_raw"],
        "images": article["images"],
        "videos": article["videos"],
        "content_hash": hashlib.md5((title + article["content_raw"]).encode("utf-8")).hexdigest(),
        "status": "raw",
    }


def scrape_sources(max_per_source: int = 10) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for source in SOURCES:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:max_per_source]:
            url = entry.get("link", "").strip()
            if not url:
                continue
            try:
                records.append(build_raw_record(source, entry))
            except Exception:
                continue
    return records


def persist_raw(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = list(records)
    init_db()
    inserted_or_updated = 0
    unique_sources = set()
    similarity_threshold = float(os.getenv("SIMILARITY_THRESHOLD", "0.85"))
    top_k = int(os.getenv("SIMILARITY_TOP_K", "5"))
    embedding_dim = MODEL_EMBEDDING_DIM

    def maybe_similarity_skip(query_vec: list[float]) -> bool:
        """
        Return True if the candidate should be skipped based on pgvector cosine similarity.
        """
        if not PGVECTOR_AVAILABLE or session_dialect != "postgresql":
            return False

        q_str = "[" + ", ".join(f"{x:.8f}" for x in query_vec) + "]"

        stmt = text(
            f"""
            -- pgvector: <=> is cosine distance. Convert it to cosine similarity in [-1, 1].
            -- Cast `embedding` to vector in case the column was created as TEXT earlier.
            SELECT 1 - (CAST(embedding AS vector({embedding_dim})) <=> CAST(:q AS vector({embedding_dim}))) AS similarity
            FROM article_embeddings
            ORDER BY CAST(embedding AS vector({embedding_dim})) <=> CAST(:q AS vector({embedding_dim}))
            LIMIT :k
            """
        )
        rows = session.execute(stmt, {"q": q_str, "k": top_k}).all()
        if not rows:
            return False

        max_similarity = max((float(r.similarity) for r in rows if r.similarity is not None), default=None)
        if max_similarity is None:
            return False
        return max_similarity > similarity_threshold

    with session_scope() as session:
        session_dialect = session.bind.dialect.name
        for record in records:
            url = (record.get("url") or "").strip()
            content_hash = (record.get("content_hash") or "").strip()

            existing_by_url = session.execute(
                select(Article.article_id, Article.content_hash).where(Article.url == url)
            ).one_or_none()

            # 1) If this URL already has the same content_hash, skip.
            if existing_by_url is not None and existing_by_url[1] == content_hash:
                continue

            # 2) If the content_hash already exists globally, skip insertion/update.
            existing_hash = session.execute(
                select(Article.article_id).where(Article.content_hash == content_hash)
            ).one_or_none()
            if existing_hash is not None:
                continue

            # 3) New candidate: compute embedding and compare to similar stored items.
            record["file_content"] = record.get("content_raw", "")
            try:
                query_vec = embed_text(record.get("content_raw", ""))
            except Exception:
                # If embedding deps aren't installed, fall back to storing raw only.
                # (Similarity gating + embeddings will be unavailable in that case.)
                upsert_article(record, session)
                inserted_or_updated += 1
                source = record.get("source")
                if source:
                    unique_sources.add(source)
                continue

            if maybe_similarity_skip(query_vec):
                continue

            # 4) Similarity not too high: upsert raw article and store embedding.
            article_id = upsert_article(record, session)

            if PGVECTOR_AVAILABLE and session_dialect == "postgresql":
                row = session.get(ArticleEmbedding, article_id)
                if row is None:
                    session.add(
                        ArticleEmbedding(
                            article_id=article_id,
                            embedding=query_vec,
                            updated_at=datetime.now(timezone.utc),
                        )
                    )
                else:
                    row.embedding = query_vec
                    row.updated_at = datetime.now(timezone.utc)

            inserted_or_updated += 1
            source = record.get("source")
            if source:
                unique_sources.add(source)

    count = inserted_or_updated
    for record in records:
        record.pop("file_content", None)
    return {
        "count": count,
        "stored_in": "postgres",
        "sources": sorted(unique_sources),
        "last_scrape_at": iso_now(),
    }

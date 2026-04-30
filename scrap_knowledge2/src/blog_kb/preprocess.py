from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from .config import STOPWORDS
from .db import Article, init_db, session_scope, upsert_cleaned_article
from .storage import iso_now


WORD_RE = re.compile(r"[A-Za-z][A-Za-z\-']{2,}")
ENTITY_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b")
NOISY_ENTITIES = {
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
}


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    text = re.sub(r"\s+([.,;:!?])", r"\1", text)
    return text


def split_sentences(text: str) -> list[str]:
    if not text:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def summarize(text: str, max_sentences: int = 3) -> str:
    sentences = split_sentences(text)
    return " ".join(sentences[:max_sentences])


def extract_keywords(text: str, limit: int = 10) -> list[str]:
    counts: Counter[str] = Counter()
    for token in WORD_RE.findall(text.lower()):
        if token not in STOPWORDS and len(token) > 3:
            counts[token] += 1
    return [word for word, _ in counts.most_common(limit)]


def extract_entities(text: str, limit: int = 12) -> list[str]:
    counts: Counter[str] = Counter()
    for match in ENTITY_RE.findall(text):
        normalized = match.strip()
        if normalized in NOISY_ENTITIES:
            continue
        if normalized.lower() not in STOPWORDS and len(normalized) > 2:
            counts[normalized] += 1
    return [entity for entity, _ in counts.most_common(limit)]


def parse_date(value: str) -> str | None:
    value = (value or "").strip()
    if not value or value == "None":
        return None

    # Normalize common timezone tokens to a numeric UTC offset so strptime can handle them.
    # Many RSS feeds use 'GMT' to mean UTC.
    if value.endswith("GMT"):
        value = value.replace("GMT", "+0000")

    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except ValueError:
            continue
    return None


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 120) -> list[str]:
    text = normalize_text(text)
    if len(text) <= chunk_size:
        return [text] if text else []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        stop = min(len(text), start + chunk_size)
        chunks.append(text[start:stop].strip())
        if stop >= len(text):
            break
        start = max(stop - overlap, start + 1)
    return [chunk for chunk in chunks if chunk]


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for record in records:
        key = record.get("content_hash") or record["article_id"]
        if key not in unique or len(record.get("content_raw", "")) > len(unique[key].get("content_raw", "")):
            unique[key] = record
    return list(unique.values())


def build_processed_record(record: dict[str, Any]) -> dict[str, Any]:
    clean_text = normalize_text(record.get("content_raw", "") or record.get("summary_raw", ""))
    summary_short = summarize(clean_text, max_sentences=2)
    summary_medium = summarize(clean_text, max_sentences=4)
    keywords = extract_keywords(clean_text)
    entities = extract_entities(clean_text)
    # Store a compact, searchable text projection in file_content.
    file_content = " | ".join(
        part for part in [record.get("title", ""), summary_short, "keywords: " + ", ".join(keywords), "entities: " + ", ".join(entities)] if part
    )
    return {
        "article_id": record["article_id"],
        "source": record.get("source", ""),
        "source_url": record.get("source_url", ""),
        "title": normalize_text(record.get("title", "")),
        "summary_raw": summary_medium or record.get("summary_raw", ""),
        "published_at": parse_date(record.get("published_at_raw", "")),
        "content_raw": clean_text,
        "images": record.get("images", []),
        "videos": record.get("videos", []),
        "status": "processed",
        "file_content": file_content,
    }


def preprocess_latest_raw() -> dict[str, Any]:
    init_db()
    raw_records = []
    with session_scope() as session:
        articles = session.execute(select(Article)).scalars().all()
        for article in articles:
            raw_records.append(
                {
                    "article_id": article.article_id,
                    "source": article.source or "",
                    "source_url": article.url or "",
                    "title": article.title or "",
                    "summary_raw": article.summary_raw or "",
                    "published_at_raw": article.published_at_raw or "",
                    "content_raw": article.content_raw or "",
                    "content_hash": article.content_hash or "",
                    "images": [row.image_url for row in article.images],
                    "videos": [row.video_url for row in article.videos],
                }
            )

        deduped = dedupe_records(raw_records)
        processed = [build_processed_record(record) for record in deduped if record.get("content_raw") or record.get("summary_raw")]
        processed_by_id = {record["article_id"]: record for record in processed}
        for article in articles:
            update = processed_by_id.get(article.article_id)
            if not update:
                continue
            article.title = update["title"]
            article.summary_raw = update["summary_raw"]
            article.content_raw = update["content_raw"]
            article.status = update["status"]
            article.file_content = update["file_content"]

        for record in processed:
            upsert_cleaned_article(record, session)

    return {
        "raw_records": len(raw_records),
        "processed_records": len(processed),
        "stored_in": "postgres",
        "processed_at": iso_now(),
    }

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    select,
    text,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


def _default_database_url() -> str:
    load_dotenv()
    raw_url = os.getenv("DATABASE_URL", "sqlite:///./blog_kb.db")
    if raw_url.startswith("postgresql://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


class Base(DeclarativeBase):
    pass


class Article(Base):
    __tablename__ = "articles"
    __table_args__ = (UniqueConstraint("url", name="uq_articles_url"),)

    article_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_category: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    published_at_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Global dedupe key: the same content_hash should not appear across different URLs.
    content_hash: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    status: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    images: Mapped[list["ArticleImage"]] = relationship(back_populates="article", cascade="all, delete-orphan")
    videos: Mapped[list["ArticleVideo"]] = relationship(back_populates="article", cascade="all, delete-orphan")


class ArticleImage(Base):
    __tablename__ = "article_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[str | None] = mapped_column(
        String(100), ForeignKey("articles.article_id", ondelete="CASCADE"), nullable=True
    )
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    article: Mapped[Article | None] = relationship(back_populates="images")


class ArticleVideo(Base):
    __tablename__ = "article_videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[str | None] = mapped_column(
        String(100), ForeignKey("articles.article_id", ondelete="CASCADE"), nullable=True
    )
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    article: Mapped[Article | None] = relationship(back_populates="videos")


# Embeddings (pgvector). Kept in a separate table so preprocessing/raw models remain unchanged.
_EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

try:
    # Optional import: unit tests run on sqlite and shouldn't fail just because pgvector isn't installed.
    from pgvector.sqlalchemy import Vector  # type: ignore
except Exception:  # pragma: no cover
    Vector = None  # type: ignore

PGVECTOR_AVAILABLE = Vector is not None


class ArticleEmbedding(Base):
    __tablename__ = "article_embeddings"

    article_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("articles.article_id", ondelete="CASCADE"),
        primary_key=True,
    )

    # On sqlite (tests), this degrades to a TEXT column if pgvector isn't available.
    embedding: Mapped[Any] = mapped_column(Vector(_EMBEDDING_DIM) if Vector else Text, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class CleanedArticle(Base):
    __tablename__ = "cleaned_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    content_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    file_content: Mapped[str | None] = mapped_column(Text, nullable=True)

    images: Mapped[list["CleanedArticleImage"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )
    videos: Mapped[list["CleanedArticleVideo"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )


class CleanedArticleImage(Base):
    __tablename__ = "cleaned_article_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[str | None] = mapped_column(
        String(100), ForeignKey("cleaned_articles.article_id", ondelete="CASCADE"), nullable=True
    )
    image_url: Mapped[str] = mapped_column(Text, nullable=False)
    article: Mapped[CleanedArticle | None] = relationship(back_populates="images")


class CleanedArticleVideo(Base):
    __tablename__ = "cleaned_article_videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    article_id: Mapped[str | None] = mapped_column(
        String(100), ForeignKey("cleaned_articles.article_id", ondelete="CASCADE"), nullable=True
    )
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    article: Mapped[CleanedArticle | None] = relationship(back_populates="videos")


_ENGINE: Engine | None = None
_SESSION_FACTORY: sessionmaker[Session] | None = None


def configure_database(database_url: str | None = None) -> None:
    global _ENGINE, _SESSION_FACTORY
    resolved = database_url or _default_database_url()
    _ENGINE = create_engine(resolved, future=True)
    _SESSION_FACTORY = sessionmaker(bind=_ENGINE, expire_on_commit=False, future=True)


def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        configure_database()
    assert _ENGINE is not None
    return _ENGINE


def _ensure_pgvector_extension() -> None:
    # pgvector extension is only available on Postgres.
    if get_engine().dialect.name != "postgresql":
        return

    with get_engine().begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def _ensure_content_hash_unique_index() -> None:
    if get_engine().dialect.name != "postgresql":
        return

    # Unique index is created outside the ORM metadata flow so this can be enforced for existing DBs
    # without relying on migrations.
    with get_engine().begin() as conn:
        conn.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS articles_content_hash_uq
                ON articles(content_hash)
                """
            )
        )


def init_db() -> None:
    _ensure_pgvector_extension()
    Base.metadata.create_all(get_engine())
    _ensure_content_hash_unique_index()


def dispose_engine() -> None:
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is not None:
        _ENGINE.dispose()
    _ENGINE = None
    _SESSION_FACTORY = None


@contextmanager
def session_scope() -> Any:
    global _SESSION_FACTORY
    if _SESSION_FACTORY is None:
        configure_database()
    assert _SESSION_FACTORY is not None
    session = _SESSION_FACTORY()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _parse_scraped_at(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str) and value:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    return datetime.now(timezone.utc).replace(tzinfo=None)


def upsert_article(record: dict[str, Any], session: Session) -> str:
    url = (record.get("url") or "").strip()
    existing = session.execute(select(Article).where(Article.url == url)).scalar_one_or_none()
    if existing is None:
        article = Article(article_id=record["article_id"], url=url)
        session.add(article)
    else:
        article = existing

    article.source = record.get("source")
    article.source_category = record.get("source_category")
    article.title = record.get("title")
    article.summary_raw = record.get("summary_raw")
    article.scraped_at = _parse_scraped_at(record.get("scraped_at"))
    article.published_at_raw = record.get("published_at_raw")
    article.content_raw = record.get("content_raw")
    article.content_hash = record.get("content_hash")
    article.status = record.get("status", "raw")
    article.file_content = record.get("file_content") or record.get("content_raw")

    article.images.clear()
    article.videos.clear()
    for image_url in record.get("images", []):
        if image_url:
            article.images.append(ArticleImage(image_url=image_url))
    for video_url in record.get("videos", []):
        if video_url:
            article.videos.append(ArticleVideo(video_url=video_url))

    session.flush()
    return article.article_id


def _parse_optional_iso_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    return None


def upsert_cleaned_article(record: dict[str, Any], session: Session) -> None:
    article_id = record["article_id"]
    existing = session.execute(
        select(CleanedArticle).where(CleanedArticle.article_id == article_id)
    ).scalar_one_or_none()
    if existing is None:
        cleaned = CleanedArticle(article_id=article_id)
        session.add(cleaned)
    else:
        cleaned = existing

    cleaned.source = record.get("source")
    cleaned.source_url = record.get("source_url")
    cleaned.title = record.get("title")
    cleaned.summary_raw = record.get("summary_raw")
    cleaned.published_at = _parse_optional_iso_datetime(record.get("published_at"))
    cleaned.content_raw = record.get("content_raw")
    cleaned.status = record.get("status")
    cleaned.file_content = record.get("file_content")

    cleaned.images.clear()
    cleaned.videos.clear()
    for image_url in record.get("images", []):
        if image_url:
            cleaned.images.append(CleanedArticleImage(image_url=image_url))
    for video_url in record.get("videos", []):
        if video_url:
            cleaned.videos.append(CleanedArticleVideo(video_url=video_url))

    session.flush()


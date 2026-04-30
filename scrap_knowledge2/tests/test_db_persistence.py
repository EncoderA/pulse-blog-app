import tempfile
import unittest
from pathlib import Path

from sqlalchemy import select

from blog_kb.db import Article, configure_database, dispose_engine, init_db, session_scope, upsert_article


class DbPersistenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tempdir.name) / "test.db"
        configure_database(f"sqlite:///{db_path}")
        init_db()

    def tearDown(self) -> None:
        dispose_engine()
        self.tempdir.cleanup()

    def test_upsert_uses_unique_url_constraint_semantics(self) -> None:
        first = {
            "article_id": "a1",
            "source": "Source1",
            "source_category": "world",
            "url": "https://example.com/a",
            "title": "Title 1",
            "summary_raw": "Summary 1",
            "scraped_at": "2026-04-28T10:00:00+00:00",
            "published_at_raw": "",
            "content_raw": "Body one",
            "content_hash": "h1",
            "status": "raw",
            "file_content": "Body one",
            "images": ["https://example.com/img1.jpg"],
            "videos": ["https://example.com/v1.mp4"],
        }
        second = {
            **first,
            "article_id": "a2",
            "title": "Title 2",
            "summary_raw": "Summary 2",
            "content_raw": "Body two",
            "content_hash": "h2",
            "images": ["https://example.com/img2.jpg"],
            "videos": [],
        }

        with session_scope() as session:
            upsert_article(first, session)
            upsert_article(second, session)

        with session_scope() as session:
            rows = session.execute(select(Article)).scalars().all()
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].url, "https://example.com/a")
            self.assertEqual(rows[0].title, "Title 2")
            self.assertEqual(rows[0].content_hash, "h2")
            self.assertEqual(len(rows[0].images), 1)
            self.assertEqual(rows[0].images[0].image_url, "https://example.com/img2.jpg")
            self.assertEqual(len(rows[0].videos), 0)


if __name__ == "__main__":
    unittest.main()

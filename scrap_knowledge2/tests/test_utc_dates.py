import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from sqlalchemy import select

from blog_kb.db import (
    CleanedArticle,
    configure_database,
    dispose_engine,
    init_db,
    session_scope,
    upsert_cleaned_article,
)


class UtcDateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        db_path = Path(self.tempdir.name) / "test.db"
        configure_database(f"sqlite:///{db_path}")
        init_db()

    def tearDown(self) -> None:
        dispose_engine()
        self.tempdir.cleanup()

    def test_cleaned_published_at_is_converted_to_naive_utc(self) -> None:
        # Input includes an offset; storage should normalize to UTC and drop tzinfo.
        record = {
            "article_id": "a1",
            "title": "t",
            "summary_raw": "s",
            "published_at": "2026-04-28T07:28:16+05:30",
            "content_raw": "body",
            "status": "processed",
            "file_content": "body",
            "images": [],
            "videos": [],
        }

        with session_scope() as session:
            upsert_cleaned_article(record, session)

        with session_scope() as session:
            row = session.execute(
                select(CleanedArticle).where(CleanedArticle.article_id == "a1")
            ).scalar_one()

            self.assertIsNone(row.published_at.tzinfo)
            self.assertEqual(row.published_at, datetime(2026, 4, 28, 1, 58, 16))


if __name__ == "__main__":
    unittest.main()


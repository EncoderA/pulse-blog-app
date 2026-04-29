import unittest

from blog_kb.preprocess import extract_keywords, normalize_text, parse_date


class PreprocessTests(unittest.TestCase):
    def test_normalize_text_compacts_whitespace(self) -> None:
        normalized = normalize_text("Hello   world . \n  This is   text.")
        self.assertEqual(normalized, "Hello world. This is text.")

    def test_extract_keywords_filters_common_words(self) -> None:
        keywords = extract_keywords("AI startup raises funding while AI platform expands cloud business", limit=5)
        self.assertIn("startup", keywords)
        self.assertIn("funding", keywords)

    def test_parse_date_understands_rss_timestamp(self) -> None:
        value = parse_date("Mon, 28 Apr 2026 07:28:16 +0000")
        self.assertEqual(value, "2026-04-28T07:28:16+00:00")


if __name__ == "__main__":
    unittest.main()

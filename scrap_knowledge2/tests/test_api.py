import unittest

from fastapi.testclient import TestClient

from blog_kb.api import app


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health_endpoint_returns_ok(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_scheduler_endpoint_returns_job_details(self) -> None:
        response = self.client.get("/scheduler")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("jobs", body)
        self.assertEqual(len(body["jobs"]), 1)

    def test_deprecated_endpoints_return_deprecation_payload(self) -> None:
        for endpoint in ("/status/latest", "/topics", "/stories", "/timeline"):
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200)
            body = response.json()
            self.assertTrue(body.get("deprecated"))

    def test_cleaned_articles_endpoint_returns_shape(self) -> None:
        response = self.client.get("/cleaned/articles?limit=10&offset=0")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn("count", body)
        self.assertIn("items", body)
        self.assertIsInstance(body["items"], list)


if __name__ == "__main__":
    unittest.main()

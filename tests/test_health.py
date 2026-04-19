"""Tests for the /health endpoint."""
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestHealth:
    """GET /health"""

    def test_health_ok(self, client: TestClient):
        with patch("app.main.check_db_health", return_value=True):
            resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "environment" in data
        assert "version" in data
        assert data["checks"]["database"] == "ok"

    def test_health_degraded_when_db_down(self, client: TestClient):
        with patch("app.main.check_db_health", return_value=False):
            resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["checks"]["database"] == "unreachable"

    def test_security_headers_present(self, client: TestClient):
        with patch("app.main.check_db_health", return_value=True):
            resp = client.get("/health")
        assert resp.headers.get("x-content-type-options") == "nosniff"
        assert resp.headers.get("x-frame-options") == "DENY"
        assert "x-request-id" in resp.headers


class TestDocs:
    """OpenAPI documentation endpoints."""

    def test_openapi_json_accessible(self, client: TestClient):
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert schema["info"]["title"] == "OneWorld API"

    def test_swagger_ui_accessible(self, client: TestClient):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_redoc_accessible(self, client: TestClient):
        resp = client.get("/redoc")
        assert resp.status_code == 200

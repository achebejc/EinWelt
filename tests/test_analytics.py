"""Unit tests for /analytics endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestCreateEvent:
    """POST /analytics/events"""

    def test_create_event_success(self, client: TestClient, auth_headers):
        resp = client.post(
            "/analytics/events",
            json={"event_name": "screen.view", "payload": {"screen": "home"}},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["detail"] == "Event recorded."

    def test_create_event_no_payload(self, client: TestClient, auth_headers):
        resp = client.post(
            "/analytics/events",
            json={"event_name": "button.tap"},
            headers=auth_headers,
        )
        assert resp.status_code == 201

    def test_empty_event_name_rejected(self, client: TestClient, auth_headers):
        resp = client.post(
            "/analytics/events",
            json={"event_name": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_event_name_too_long_rejected(self, client: TestClient, auth_headers):
        resp = client.post(
            "/analytics/events",
            json={"event_name": "x" * 256},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_unauthenticated_returns_401(self, client: TestClient):
        resp = client.post(
            "/analytics/events",
            json={"event_name": "screen.view"},
        )
        assert resp.status_code == 401

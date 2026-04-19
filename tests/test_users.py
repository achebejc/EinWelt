"""Unit tests for /users endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import make_user
from app.core.security import create_access_token


class TestGetMe:
    """GET /users/me"""

    def test_returns_current_user(self, client: TestClient, test_user, auth_headers):
        resp = client.get("/users/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert "id" in data
        assert "hashed_password" not in data

    def test_unauthenticated_returns_401(self, client: TestClient):
        resp = client.get("/users/me")
        assert resp.status_code == 401

    def test_invalid_token_returns_401(self, client: TestClient):
        resp = client.get("/users/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401


class TestUpdateMe:
    """PATCH /users/me"""

    def test_update_full_name(self, client: TestClient, db: Session, test_user, auth_headers):
        resp = client.patch(
            "/users/me",
            json={"full_name": "Updated Name"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Name"

    def test_empty_full_name_rejected(self, client: TestClient, auth_headers):
        resp = client.patch(
            "/users/me",
            json={"full_name": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_too_long_full_name_rejected(self, client: TestClient, auth_headers):
        resp = client.patch(
            "/users/me",
            json={"full_name": "A" * 256},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_unauthenticated_returns_401(self, client: TestClient):
        resp = client.patch("/users/me", json={"full_name": "Name"})
        assert resp.status_code == 401

"""Unit tests for /auth endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import make_user


class TestRegister:
    """POST /auth/register"""

    def test_register_owner_success(self, client: TestClient, db: Session, monkeypatch):
        # Patch owner email to match what we send
        monkeypatch.setattr("app.core.config.settings.owner_email", "ceo@oneworld.app")
        # Patch send_email so no real SMTP call is made
        monkeypatch.setattr("app.Api.routes.auth.send_email", lambda *a, **kw: None)

        resp = client.post(
            "/auth/register",
            json={
                "email": "ceo@oneworld.app",
                "password": "Str0ng!Pass1",
                "full_name": "Jessica Achebe",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_non_owner_forbidden(self, client: TestClient, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.owner_email", "ceo@oneworld.app")
        resp = client.post(
            "/auth/register",
            json={
                "email": "other@example.com",
                "password": "Str0ng!Pass1",
                "full_name": "Other User",
            },
        )
        assert resp.status_code == 403

    def test_register_weak_password_rejected(self, client: TestClient, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.owner_email", "ceo@oneworld.app")
        resp = client.post(
            "/auth/register",
            json={
                "email": "ceo@oneworld.app",
                "password": "weak",
                "full_name": "Jessica",
            },
        )
        assert resp.status_code == 422

    def test_register_duplicate_email_conflict(self, client: TestClient, db: Session, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.owner_email", "ceo@oneworld.app")
        monkeypatch.setattr("app.Api.routes.auth.send_email", lambda *a, **kw: None)
        make_user(db, email="ceo@oneworld.app", is_owner=True)

        resp = client.post(
            "/auth/register",
            json={
                "email": "ceo@oneworld.app",
                "password": "Str0ng!Pass1",
                "full_name": "Jessica",
            },
        )
        assert resp.status_code == 409


class TestLogin:
    """POST /auth/login"""

    def test_login_success(self, client: TestClient, db: Session):
        make_user(db, email="user@example.com", password="Test1234!")
        resp = client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "Test1234!"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client: TestClient, db: Session):
        make_user(db, email="user2@example.com", password="Test1234!")
        resp = client.post(
            "/auth/login",
            json={"email": "user2@example.com", "password": "WrongPass!"},
        )
        assert resp.status_code == 401

    def test_login_unknown_email(self, client: TestClient):
        resp = client.post(
            "/auth/login",
            json={"email": "nobody@example.com", "password": "Test1234!"},
        )
        assert resp.status_code == 401

    def test_login_invalid_email_format(self, client: TestClient):
        resp = client.post(
            "/auth/login",
            json={"email": "not-an-email", "password": "Test1234!"},
        )
        assert resp.status_code == 422


class TestForgotPassword:
    """POST /auth/forgot-password"""

    def test_always_returns_202(self, client: TestClient, monkeypatch):
        monkeypatch.setattr("app.Api.routes.auth.send_email", lambda *a, **kw: None)
        resp = client.post(
            "/auth/forgot-password",
            json={"email": "anyone@example.com"},
        )
        assert resp.status_code == 202

    def test_sends_email_for_known_user(self, client: TestClient, db: Session, monkeypatch):
        make_user(db, email="known@example.com")
        sent = []
        monkeypatch.setattr(
            "app.Api.routes.auth.send_email",
            lambda to, subj, body: sent.append(to),
        )
        client.post("/auth/forgot-password", json={"email": "known@example.com"})
        assert "known@example.com" in sent


class TestVerifyEmail:
    """POST /auth/verify-email"""

    def test_invalid_token_returns_400(self, client: TestClient):
        resp = client.post("/auth/verify-email", json={"token": "invalid-token"})
        assert resp.status_code == 400


class TestResetPassword:
    """POST /auth/reset-password"""

    def test_invalid_token_returns_400(self, client: TestClient):
        resp = client.post(
            "/auth/reset-password",
            json={"token": "bad-token", "new_password": "N3wStr0ng!Pass"},
        )
        assert resp.status_code == 400

    def test_weak_new_password_rejected(self, client: TestClient):
        resp = client.post(
            "/auth/reset-password",
            json={"token": "any-token", "new_password": "weak"},
        )
        assert resp.status_code == 422

"""Unit tests for /utility endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock


class TestChat:
    """POST /utility/chat"""

    def test_chat_unauthenticated_returns_401(self, client: TestClient):
        resp = client.post("/utility/chat", json={"message": "Hello"})
        assert resp.status_code == 401

    def test_chat_openai_not_configured_returns_503(
        self, client: TestClient, auth_headers, monkeypatch
    ):
        monkeypatch.setattr("app.core.config.settings.openai_api_key", None)
        resp = client.post(
            "/utility/chat",
            json={"message": "Hello", "language": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 503

    def test_chat_empty_message_rejected(self, client: TestClient, auth_headers):
        resp = client.post(
            "/utility/chat",
            json={"message": "", "language": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_chat_message_too_long_rejected(self, client: TestClient, auth_headers):
        resp = client.post(
            "/utility/chat",
            json={"message": "x" * 4001, "language": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_chat_success(self, client: TestClient, auth_headers, monkeypatch):
        monkeypatch.setattr("app.core.config.settings.openai_api_key", "sk-fake")

        mock_choice = MagicMock()
        mock_choice.message.content = "Hello! How can I help?"
        mock_completion = MagicMock()
        mock_completion.choices = [mock_choice]

        async def fake_create(**kwargs):
            return mock_completion

        with patch(
            "app.services.ai_router.AsyncOpenAI"
        ) as mock_client_cls:
            mock_instance = MagicMock()
            mock_instance.chat.completions.create = fake_create
            mock_client_cls.return_value = mock_instance

            resp = client.post(
                "/utility/chat",
                json={"message": "Hello", "language": "en"},
                headers=auth_headers,
            )

        assert resp.status_code == 200
        data = resp.json()
        assert "response" in data
        assert data["language"] == "en"


class TestScan:
    """POST /utility/scan"""

    def test_scan_unauthenticated_returns_401(self, client: TestClient):
        resp = client.post("/utility/scan", json={"extracted_text": "some text"})
        assert resp.status_code == 401

    def test_scan_empty_text_rejected(self, client: TestClient, auth_headers):
        resp = client.post(
            "/utility/scan",
            json={"extracted_text": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestTranslate:
    """POST /utility/translate"""

    def test_translate_unauthenticated_returns_401(self, client: TestClient):
        resp = client.post(
            "/utility/translate",
            json={"text": "Hello", "targetLanguage": "de"},
        )
        assert resp.status_code == 401

    def test_translate_missing_target_language_rejected(
        self, client: TestClient, auth_headers
    ):
        resp = client.post(
            "/utility/translate",
            json={"text": "Hello"},
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestBudget:
    """POST /utility/budget"""

    def test_budget_unauthenticated_returns_401(self, client: TestClient):
        resp = client.post(
            "/utility/budget",
            json={"income": 3000.0, "expenses": 2000.0},
        )
        assert resp.status_code == 401

    def test_budget_negative_income_rejected(self, client: TestClient, auth_headers):
        resp = client.post(
            "/utility/budget",
            json={"income": -100.0, "expenses": 500.0},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_budget_negative_expenses_rejected(self, client: TestClient, auth_headers):
        resp = client.post(
            "/utility/budget",
            json={"income": 3000.0, "expenses": -1.0},
            headers=auth_headers,
        )
        assert resp.status_code == 422

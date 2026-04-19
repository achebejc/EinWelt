"""Unit tests for /billing endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestCheckout:
    """POST /billing/checkout"""

    def test_checkout_unauthenticated_returns_401(self, client: TestClient):
        resp = client.post("/billing/checkout")
        assert resp.status_code == 401

    def test_checkout_stripe_not_configured_returns_503(
        self, client: TestClient, auth_headers, monkeypatch
    ):
        monkeypatch.setattr("app.core.config.settings.stripe_secret_key", None)
        monkeypatch.setattr("app.core.config.settings.stripe_price_id", None)
        resp = client.post("/billing/checkout", headers=auth_headers)
        assert resp.status_code == 503

    def test_checkout_returns_url_when_stripe_configured(
        self, client: TestClient, auth_headers, monkeypatch
    ):
        monkeypatch.setattr("app.core.config.settings.stripe_secret_key", "sk_test_fake")
        monkeypatch.setattr("app.core.config.settings.stripe_price_id", "price_fake")

        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/pay/fake"

        with patch("app.services.billing.stripe.checkout.Session.create", return_value=mock_session):
            resp = client.post("/billing/checkout", headers=auth_headers)

        assert resp.status_code == 200
        assert resp.json()["checkout_url"] == "https://checkout.stripe.com/pay/fake"

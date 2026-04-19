"""Unit tests for app/core/security.py."""
import pytest
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_token,
)


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        hashed = get_password_hash("MySecret1!")
        assert hashed != "MySecret1!"

    def test_verify_correct_password(self):
        hashed = get_password_hash("MySecret1!")
        assert verify_password("MySecret1!", hashed) is True

    def test_verify_wrong_password(self):
        hashed = get_password_hash("MySecret1!")
        assert verify_password("WrongPass!", hashed) is False

    def test_same_password_produces_different_hashes(self):
        h1 = get_password_hash("MySecret1!")
        h2 = get_password_hash("MySecret1!")
        assert h1 != h2  # bcrypt uses random salt


class TestJWT:
    def test_create_and_decode_token(self):
        token = create_access_token("user-123")
        payload = decode_token(token)
        assert payload["sub"] == "user-123"

    def test_expired_token_raises(self):
        token = create_access_token("user-123", expires_delta=timedelta(seconds=-1))
        with pytest.raises(ValueError):
            decode_token(token)

    def test_tampered_token_raises(self):
        token = create_access_token("user-123")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(ValueError):
            decode_token(tampered)

    def test_garbage_token_raises(self):
        with pytest.raises(ValueError):
            decode_token("not.a.jwt")

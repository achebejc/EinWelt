"""Integration tests for database operations."""
import uuid
import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.token import Token
from app.models.analytics import AnalyticsEvent
from app.core.security import get_password_hash
from app.services.tokens import create_token, consume_token
from tests.conftest import make_user


@pytest.mark.integration
class TestUserModel:
    def test_create_and_retrieve_user(self, db: Session):
        user = make_user(db, email="db_test@example.com")
        fetched = db.query(User).filter(User.email == "db_test@example.com").first()
        assert fetched is not None
        assert fetched.id == user.id
        assert fetched.full_name == user.full_name

    def test_email_uniqueness_enforced(self, db: Session):
        make_user(db, email="unique@example.com")
        from sqlalchemy.exc import IntegrityError
        with pytest.raises(IntegrityError):
            duplicate = User(
                id=uuid.uuid4(),
                email="unique@example.com",
                hashed_password=get_password_hash("Test1234!"),
                full_name="Duplicate",
            )
            db.add(duplicate)
            db.flush()

    def test_user_defaults(self, db: Session):
        user = make_user(db, email="defaults@example.com")
        assert user.is_owner is False
        assert user.is_verified is True  # make_user sets is_verified=True by default
        assert user.created_at is not None


@pytest.mark.integration
class TestTokenModel:
    def test_create_token(self, db: Session):
        user = make_user(db, email="token_user@example.com")
        token = create_token(db, user.id, "verify_email", minutes_valid=60)
        assert token.id is not None
        assert token.token_type == "verify_email"
        assert len(token.token) > 0

    def test_consume_token_removes_it(self, db: Session):
        user = make_user(db, email="consume_user@example.com")
        token = create_token(db, user.id, "reset_password", minutes_valid=60)
        raw = token.token

        result = consume_token(db, raw, "reset_password")
        assert result is not None
        assert result.user_id == user.id

        # Token should be gone now
        gone = db.query(Token).filter(Token.token == raw).first()
        assert gone is None

    def test_consume_wrong_type_returns_none(self, db: Session):
        user = make_user(db, email="wrongtype_user@example.com")
        token = create_token(db, user.id, "verify_email", minutes_valid=60)
        result = consume_token(db, token.token, "reset_password")
        assert result is None

    def test_consume_nonexistent_token_returns_none(self, db: Session):
        result = consume_token(db, "nonexistent-token-value", "verify_email")
        assert result is None


@pytest.mark.integration
class TestAnalyticsEventModel:
    def test_create_analytics_event(self, db: Session):
        import json
        user = make_user(db, email="analytics_user@example.com")
        event = AnalyticsEvent(
            user_id=user.id,
            event_name="screen.view",
            payload_json=json.dumps({"screen": "home"}),
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        fetched = db.query(AnalyticsEvent).filter(
            AnalyticsEvent.user_id == user.id
        ).first()
        assert fetched is not None
        assert fetched.event_name == "screen.view"
        assert json.loads(fetched.payload_json)["screen"] == "home"

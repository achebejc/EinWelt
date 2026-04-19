import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.token import Token


def create_token(
    db: Session,
    user_id: uuid.UUID,
    token_type: str,
    minutes_valid: int = 60,
) -> Token:
    """Generate a secure random token, persist it, and return the ORM object."""
    raw = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes_valid)
    token = Token(
        user_id=user_id,
        token=raw,
        token_type=token_type,
        expires_at=expires_at,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def consume_token(db: Session, token_str: str, token_type: str) -> Optional[Token]:
    """
    Look up a token by value and type.  Returns the Token if it is valid and
    not yet expired, then deletes it so it cannot be reused.  Returns None if
    the token is missing or expired.
    """
    token = (
        db.query(Token)
        .filter(Token.token == token_str, Token.token_type == token_type)
        .first()
    )
    if token is None:
        return None
    if token.expires_at < datetime.now(timezone.utc):
        db.delete(token)
        db.commit()
        return None
    db.delete(token)
    db.commit()
    return token

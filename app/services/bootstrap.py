from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User


def ensure_owner_account(db: Session) -> None:
    """
    Create the default owner account on first startup if no owner exists yet.
    Safe to call on every startup — it is a no-op when the owner already exists.
    """
    existing = db.query(User).filter(User.is_owner.is_(True)).first()
    if existing:
        return

    owner = User(
        email=settings.owner_email,
        hashed_password=get_password_hash(settings.owner_password),
        full_name=settings.owner_full_name,
        is_owner=True,
        is_verified=True,
    )
    db.add(owner)
    db.commit()
    print(f"[bootstrap] Owner account created: {settings.owner_email}")

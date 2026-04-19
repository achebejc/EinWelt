from fastapi import HTTPException, status

# from fastapi.security import OAuth2PasswordBearer  # requires app.models.user
# from jose import JWTError, jwt  # requires app.models.user
# from sqlalchemy.orm import Session  # requires models
# from app.core.config import settings  # used by JWT decode
# from app.db.session import get_db  # requires models
# from app.models.user import User  # not yet implemented

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user():
    # Placeholder — returns 401 until app.models.user is implemented
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication not yet implemented",
        headers={"WWW-Authenticate": "Bearer"},
    )

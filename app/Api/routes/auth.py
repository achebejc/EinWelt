from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services.email import send_email
from app.services.tokens import consume_token, create_token

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def register(request: Request, body: RegisterRequest, db: Session = Depends(get_db)):
    """Owner-only registration: only the configured owner e-mail is allowed."""
    if body.email.lower() != settings.owner_email.lower():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is disabled for this deployment.",
        )
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this e-mail already exists.",
        )
    user = User(
        email=body.email.lower(),
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        is_owner=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification e-mail
    token_obj = create_token(db, user.id, "verify_email", minutes_valid=1440)
    verify_url = f"{settings.app_base_url}/auth/verify-email?token={token_obj.token}"
    send_email(
        user.email,
        "Verify your EinWelt account",
        f"Click the link to verify your e-mail address:\n\n{verify_url}",
    )

    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect e-mail or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("10/minute")
def forgot_password(request: Request, body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if user:
        token_obj = create_token(db, user.id, "reset_password", minutes_valid=60)
        reset_url = f"{settings.app_base_url}/auth/reset-password?token={token_obj.token}"
        send_email(
            user.email,
            "Reset your EinWelt password",
            f"Click the link to reset your password (valid for 1 hour):\n\n{reset_url}",
        )
    # Always return 202 to avoid leaking whether the e-mail exists
    return {"detail": "If that e-mail is registered you will receive a reset link shortly."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def reset_password(request: Request, body: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_obj = consume_token(db, body.token, "reset_password")
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )
    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.hashed_password = get_password_hash(body.new_password)
    db.commit()
    return {"detail": "Password updated successfully."}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
def verify_email(request: Request, body: VerifyEmailRequest, db: Session = Depends(get_db)):
    token_obj = consume_token(db, body.token, "verify_email")
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )
    user = db.query(User).filter(User.id == token_obj.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    user.is_verified = True
    db.commit()
    return {"detail": "E-mail verified successfully."}

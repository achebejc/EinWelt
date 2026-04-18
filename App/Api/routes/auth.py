from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from App.core.rate_limit import limiter
from App.db.session import get_db
from App.models.user import User
from App.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest
)
from App.core.security import get_password_hash, verify_password, create_access_token
from App.services.tokens import create_token, consume_token
from App.services.email import send_email
from App.core.config import settings

router = APIRouter()

@router.post("/register")
@limiter.limit("10/minute")
def register(request: Request):
    raise HTTPException(status_code=403, detail="Public registration is disabled for this deployment")

@router.post("/login", response_model=TokenResponse)
@limiter.limit("20/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user.is_owner:
        raise HTTPException(status_code=403, detail="Only the CEO owner account can access this deployment")
    return TokenResponse(access_token=create_access_token(str(user.id)))

@router.post("/forgot-password")
@limiter.limit("10/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        token = create_token(db, user.id, "reset_password", minutes_valid=30)
        reset_link = f"{settings.frontend_url}/reset-password?token={token.token}"
        try:
            send_email(user.email, "Reset your OneWorld password", f"Open this link to reset your password: {reset_link}")
        except Exception:
            pass
    return {"message": "If that email exists, a reset link was sent."}

@router.post("/reset-password")
@limiter.limit("10/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token = consume_token(db, payload.token, "reset_password")
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.get(User, token.user_id)
    user.hashed_password = get_password_hash(payload.new_password)
    db.add(user)
    db.commit()
    return {"message": "Password reset successful"}

@router.post("/verify-email")
@limiter.limit("20/minute")
def verify_email(request: Request, payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    token = consume_token(db, payload.token, "verify_email")
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.get(User, token.user_id)
    user.is_verified = True
    db.add(user)
    db.commit()
    return {"message": "Email verified"}

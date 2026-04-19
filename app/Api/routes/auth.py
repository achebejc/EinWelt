from fastapi import APIRouter, HTTPException

# from app.core.rate_limit import limiter  # not yet implemented
# from app.db.session import get_db  # requires models
# from app.models.user import User  # not yet implemented
# from app.schemas.auth import (  # not yet implemented
#     RegisterRequest, LoginRequest, TokenResponse,
#     ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest
# )
# from app.core.security import get_password_hash, verify_password, create_access_token  # not yet implemented
# from app.services.tokens import create_token, consume_token  # not yet implemented
# from app.services.email import send_email  # not yet implemented
# from app.core.config import settings

router = APIRouter()


@router.post("/register")
# @limiter.limit("10/minute")
def register():
    raise HTTPException(status_code=403, detail="Public registration is disabled for this deployment")


@router.post("/login")
# @limiter.limit("20/minute")
def login():
    return {"message": "Not implemented"}


@router.post("/forgot-password")
# @limiter.limit("10/minute")
def forgot_password():
    return {"message": "Not implemented"}


@router.post("/reset-password")
# @limiter.limit("10/minute")
def reset_password():
    return {"message": "Not implemented"}


@router.post("/verify-email")
# @limiter.limit("20/minute")
def verify_email():
    return {"message": "Not implemented"}

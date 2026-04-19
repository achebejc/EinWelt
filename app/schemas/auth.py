import re

from pydantic import BaseModel, EmailStr, Field, field_validator

# Password must be ≥8 chars, contain upper, lower, digit, and special char
_PASSWORD_RE = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,128}$"
)


def _validate_password(value: str) -> str:
    if not _PASSWORD_RE.match(value):
        raise ValueError(
            "Password must be 8–128 characters and include at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )
    return value


class RegisterRequest(BaseModel):
    """Payload for the owner registration endpoint."""

    email: EmailStr = Field(..., description="Valid e-mail address", examples=["ceo@oneworld.app"])
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Strong password (upper, lower, digit, special char required)",
        examples=["Str0ng!Pass"],
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Display name",
        examples=["Jessica Achebe"],
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password(v)


class LoginRequest(BaseModel):
    """Payload for the login endpoint."""

    email: EmailStr = Field(..., description="Registered e-mail address")
    password: str = Field(..., min_length=1, max_length=128, description="Account password")


class TokenResponse(BaseModel):
    """JWT bearer token returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    """Payload to trigger a password-reset e-mail."""

    email: EmailStr = Field(..., description="E-mail address of the account to reset")


class ResetPasswordRequest(BaseModel):
    """Payload to complete a password reset using a one-time token."""

    token: str = Field(..., min_length=1, max_length=512, description="One-time reset token")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New strong password",
        examples=["N3wStr0ng!Pass"],
    )

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password(v)


class VerifyEmailRequest(BaseModel):
    """Payload to verify an e-mail address using a one-time token."""

    token: str = Field(..., min_length=1, max_length=512, description="One-time verification token")


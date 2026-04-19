import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    """Public representation of a user account."""

    id: uuid.UUID = Field(..., description="Unique user identifier")
    email: EmailStr = Field(..., description="User's e-mail address")
    full_name: str = Field(..., description="User's display name")
    is_owner: bool = Field(..., description="Whether the user has owner privileges")
    is_verified: bool = Field(..., description="Whether the e-mail address has been verified")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC)")

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    """Payload for updating the authenticated user's profile."""

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="New display name",
        examples=["Jessica Achebe"],
    )


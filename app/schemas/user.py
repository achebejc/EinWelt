import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_owner: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    full_name: str

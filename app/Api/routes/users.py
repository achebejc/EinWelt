from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.Api.deps import get_current_user
from app.core.cache import cache_delete, cache_get, cache_set
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UpdateProfileRequest, UserOut

router = APIRouter()

_PROFILE_TTL = 300  # 5 minutes


def _profile_cache_key(user_id: str) -> str:
    return f"user:profile:{user_id}"


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
    description="Returns the authenticated user's profile. Result is cached for 5 minutes.",
)
def me(current_user: User = Depends(get_current_user)):
    key = _profile_cache_key(str(current_user.id))
    cached = cache_get(key)
    if cached:
        return cached
    out = UserOut.model_validate(current_user)
    cache_set(key, out.model_dump(mode="json"), ttl=_PROFILE_TTL)
    return out


@router.patch(
    "/me",
    response_model=UserOut,
    summary="Update current user profile",
    description="Update the authenticated user's display name.",
)
def update_me(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.full_name = body.full_name
    db.commit()
    db.refresh(current_user)
    # Invalidate cached profile
    cache_delete(_profile_cache_key(str(current_user.id)))
    return current_user


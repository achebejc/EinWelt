from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from App.Api.deps import get_current_user
from App.db.session import get_db
from App.models.user import User
from App.schemas.user import UserOut, UpdateProfileRequest

router = APIRouter()

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    current_user.full_name = payload.full_name
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

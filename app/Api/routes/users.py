from fastapi import APIRouter

# from app.Api.deps import get_current_user  # requires app.models.user
# from app.db.session import get_db  # requires models
# from app.models.user import User  # not yet implemented
# from app.schemas.user import UserOut, UpdateProfileRequest  # not yet implemented

router = APIRouter()


@router.get("/me")
def me():
    return {"message": "Not implemented"}


@router.patch("/me")
def update_me():
    return {"message": "Not implemented"}

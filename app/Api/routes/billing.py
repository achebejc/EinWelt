from fastapi import APIRouter

# from app.Api.deps import get_current_user  # requires app.models.user
# from app.models.user import User  # not yet implemented
# from app.services.billing import create_checkout_session  # not yet implemented

router = APIRouter()


@router.post("/checkout")
def checkout():
    return {"message": "Not implemented"}

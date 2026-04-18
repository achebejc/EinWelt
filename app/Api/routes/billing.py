from fastapi import APIRouter, Depends, HTTPException
from app.Api.deps import get_current_user
from app.models.user import User
from app.services.billing import create_checkout_session

router = APIRouter()

@router.post("/checkout")
def checkout(current_user: User = Depends(get_current_user)):
    try:
        session = create_checkout_session(current_user.email)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"url": session.url}

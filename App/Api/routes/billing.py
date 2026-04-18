from fastapi import APIRouter, Depends, HTTPException
from App.Api.deps import get_current_user
from App.models.user import User
from App.services.billing import create_checkout_session

router = APIRouter()

@router.post("/checkout")
def checkout(current_user: User = Depends(get_current_user)):
    try:
        session = create_checkout_session(current_user.email)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"url": session.url}

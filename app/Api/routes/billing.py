from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.Api.deps import get_current_user
from app.models.user import User
from app.services.billing import create_checkout_session

router = APIRouter()


@router.post(
    "/checkout",
    summary="Create Stripe Checkout Session",
    description=(
        "Creates a Stripe Checkout Session for the authenticated user and returns "
        "the redirect URL. Requires `STRIPE_SECRET_KEY` and `STRIPE_PRICE_ID` to be configured."
    ),
)
def checkout(current_user: User = Depends(get_current_user)):
    url = create_checkout_session(current_user.email)
    return JSONResponse({"checkout_url": url})

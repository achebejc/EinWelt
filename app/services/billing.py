import stripe
from fastapi import HTTPException, status

from app.core.config import settings


def create_checkout_session(email: str) -> str:
    """
    Create a Stripe Checkout Session for the given customer e-mail and return
    the session URL that the client should redirect to.

    Raises HTTP 503 when Stripe is not configured, and HTTP 502 when the
    Stripe API call fails.
    """
    if not settings.stripe_secret_key or not settings.stripe_price_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Billing is not configured on this server.",
        )

    stripe.api_key = settings.stripe_secret_key

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            customer_email=email,
            line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
            success_url=f"{settings.app_base_url}/billing/success",
            cancel_url=f"{settings.app_base_url}/billing/cancel",
        )
    except stripe.StripeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Stripe error: {exc.user_message}",
        ) from exc

    return session.url

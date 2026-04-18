from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.core.config import settings
from app.core.sentry import init_sentry
from app.core.rate_limit import limiter
from app.api.routes import auth, users, billing, analytics, utility
from app.db.session import SessionLocal
from app.services.bootstrap import ensure_owner_account

init_sentry()

app = FastAPI(title=settings.app_name)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(utility.router, prefix="/utility", tags=["utility"])


@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}


@app.on_event("startup")
def seed_owner_account():
    db = SessionLocal()
    try:
        ensure_owner_account(db)
    finally:
        db.close()


import logging
import time
import uuid as _uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.core.logging import configure_logging
from app.core.sentry import init_sentry
from app.core.rate_limit import limiter
from app.Api.routes import auth, users, billing, analytics, utility
from app.db.session import SessionLocal, check_db_health
from app.services.bootstrap import ensure_owner_account

# ── Logging & Sentry ──────────────────────────────────────────────────────────
configure_logging()
logger = logging.getLogger(__name__)
init_sentry()

# ── FastAPI application ───────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "OneWorld API — multilingual financial assistant backend. "
        "All endpoints require a Bearer JWT unless noted otherwise."
    ),
    openapi_tags=[
        {"name": "auth", "description": "Registration, login, e-mail verification, password reset"},
        {"name": "users", "description": "Authenticated user profile management"},
        {"name": "billing", "description": "Stripe checkout and subscription management"},
        {"name": "analytics", "description": "Client-side event ingestion"},
        {"name": "utility", "description": "AI-powered chat, scan, translate, and budget endpoints"},
        {"name": "system", "description": "Health checks and system status"},
    ],
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── Rate limiting ─────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# ── Response compression (Gzip + Brotli via GZipMiddleware) ──────────────────
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-Request-ID"],
)


# ── Security headers + request ID + access logging middleware ─────────────────
@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next) -> Response:
    # Assign a unique request ID for tracing
    request_id = request.headers.get("X-Request-ID") or str(_uuid.uuid4())

    # Enforce request body size limit
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_size:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large."},
        )

    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    # Security headers
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"

    # Structured access log
    logger.info(
        "request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": request.client.host if request.client else "unknown",
        },
    )
    return response


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(billing.router, prefix="/billing", tags=["billing"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(utility.router, prefix="/utility", tags=["utility"])


# ── Health check ──────────────────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["system"],
    summary="Health check",
    description="Returns the application status and basic dependency health.",
)
def health():
    db_ok = check_db_health()
    return {
        "status": "ok" if db_ok else "degraded",
        "environment": settings.environment,
        "version": settings.app_version,
        "checks": {
            "database": "ok" if db_ok else "unreachable",
        },
    }


# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
def seed_owner_account():
    logger.info("startup: seeding owner account if absent")
    db = SessionLocal()
    try:
        ensure_owner_account(db)
    finally:
        db.close()


# ── Graceful shutdown ─────────────────────────────────────────────────────────
@app.on_event("shutdown")
def on_shutdown():
    logger.info("shutdown: disposing database connection pool")
    from app.db.session import engine
    engine.dispose()


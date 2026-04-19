import sentry_sdk
from app.core.config import settings


def init_sentry() -> None:
    """Initialise Sentry if SENTRY_DSN is configured."""
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.2,
        )

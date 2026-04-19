import sys
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = "OneWorld API"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"

    # ── Security ──────────────────────────────────────────────────────────────
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 10080  # 7 days
    # Maximum request body size in bytes (default 1 MB)
    max_request_size: int = 1_048_576

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str
    # SQLAlchemy connection pool settings
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800  # recycle connections every 30 min

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str
    # Default TTL for cached values (seconds)
    cache_ttl: int = 300

    # ── URLs ──────────────────────────────────────────────────────────────────
    frontend_url: str = "http://localhost:19006"
    app_base_url: str = "http://localhost:8000"

    # ── SMTP ──────────────────────────────────────────────────────────────────
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "no-reply@oneworld.app"
    smtp_use_tls: bool = True

    # ── Stripe ────────────────────────────────────────────────────────────────
    stripe_secret_key: str | None = None
    stripe_price_id: str | None = None
    stripe_webhook_secret: str | None = None

    # ── Observability ─────────────────────────────────────────────────────────
    sentry_dsn: str | None = None
    log_level: str = "INFO"
    log_json: bool = False  # set True in production for structured JSON logs

    # ── AI ────────────────────────────────────────────────────────────────────
    openai_api_key: str | None = None

    # ── Owner bootstrap ───────────────────────────────────────────────────────
    owner_email: str = "ceo@oneworld.app"
    owner_password: str = "ChangeThisOwnerPassword123!"
    owner_full_name: str = "Jessica Chekwube Achebe"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # ── Validators ────────────────────────────────────────────────────────────

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_not_be_default(cls, v: str) -> str:
        if v == "change-me":
            import warnings
            warnings.warn(
                "SECRET_KEY is set to the insecure default 'change-me'. "
                "Set a strong random value in production.",
                stacklevel=2,
            )
        return v

    @model_validator(mode="after")
    def warn_production_defaults(self) -> "Settings":
        if self.environment == "production":
            issues: list[str] = []
            if self.secret_key == "change-me":
                issues.append("SECRET_KEY is the insecure default")
            if self.owner_password == "ChangeThisOwnerPassword123!":
                issues.append("OWNER_PASSWORD is the insecure default")
            if issues:
                print(
                    f"[config] CRITICAL — production environment has insecure defaults: "
                    f"{', '.join(issues)}",
                    file=sys.stderr,
                )
        return self


settings = Settings()


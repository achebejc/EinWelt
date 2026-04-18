from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "OneWorld API"
    environment: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 10080

    database_url: str
    redis_url: str

    frontend_url: str = "http://localhost:19006"
    app_base_url: str = "http://localhost:8000"

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "no-reply@oneworld.app"
    smtp_use_tls: bool = True

    stripe_secret_key: str | None = None
    stripe_price_id: str | None = None
    stripe_webhook_secret: str | None = None

    sentry_dsn: str | None = None
    openai_api_key: str | None = None

    owner_email: str = "ceo@oneworld.app"
    owner_password: str = "ChangeThisOwnerPassword123!"
    owner_full_name: str = "Jessica Chekwube Achebe"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

settings = Settings()

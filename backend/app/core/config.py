"""
Application configuration.

All secrets/config are read from environment variables (see .env.example).
Nothing sensitive is hardcoded here.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "OffPeak"
    ENV: str = "development"

    # Swappable data layer: defaults to local Postgres for the hackathon,
    # but any SQLAlchemy-compatible URL (incl. SQLite for quick local dev) works.
    DATABASE_URL: str = "postgresql+psycopg2://postgres:offpeak_dev@localhost:5432/offpeak"

    JWT_SECRET: str = "dev-secret-change-me-in-prod-please"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days, fine for a demo

    # Business rules — kept in config so they're easy to tune/replace.
    PLATFORM_COMMISSION_RATE: str = "0.10"  # Decimal string, parsed where used
    LOYALTY_POINTS_PER_DOLLAR: int = 1
    LOYALTY_POINTS_PER_CREDIT: int = 500
    LOYALTY_CREDIT_VALUE_CENTS: int = 1000  # $10.00

    # Demo/dev-mode OTP. In production this would be swapped for a real
    # SMS provider (Twilio etc.) behind the same service interface.
    OTP_DEV_MODE: bool = True
    OTP_STATIC_CODE: str = "123456"

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]


settings = Settings()

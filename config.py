"""
Application configuration. All settings can be overridden via environment variables.

BEGINNER TIP: Copy .env.example to .env and set SECRET_KEY for production.
Never commit .env or put real secrets in code!
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Settings loaded from env vars or defaults. See .env.example for options."""

    # Secret key for signing JWTs. In production: use a long random string from env.
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    # Algorithm used to sign the JWT. HS256 = symmetric key (same key signs and verifies).
    ALGORITHM: str = "HS256"
    # Access token lifetime in minutes. After this, the user must log in again.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Single instance used across the app (import: from config import settings)
settings = Settings()

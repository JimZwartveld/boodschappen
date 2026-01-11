"""Application configuration."""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "sqlite:///data/groceries.db"

    # API
    api_token: str = ""
    cors_origins: str = "*"
    log_level: str = "info"

    # App
    api_base_url: str = "http://localhost:8000"

    # Albert Heijn integration
    ah_email: str = ""
    ah_password: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

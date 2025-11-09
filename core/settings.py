"""Application settings using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str
    # Individual postgres fields are optional if DATABASE_URL is provided
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None

    # Application Settings
    debug: bool
    log_level: str
    secret_key: str
    api_v1_prefix: str

    # AI Configuration (Gemini)
    gemini_api_key: str
    gemini_model: str

    # Server Configuration
    host: str
    port: int

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()


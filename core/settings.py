"""Application settings using Pydantic BaseSettings.

This module provides type-safe configuration management using Pydantic's
BaseSettings, which automatically loads values from environment variables
and .env files. All configuration values are validated at startup.

Example:
    Settings are automatically loaded from environment variables:
    ```python
    from core.settings import settings
    print(settings.database_url)
    ```
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    This class defines all application configuration settings that are
    loaded from environment variables or a .env file. Settings are
    validated at initialization time.
    
    Attributes:
        database_url: PostgreSQL database connection URL
        postgres_user: PostgreSQL username (optional if DATABASE_URL provided)
        postgres_password: PostgreSQL password (optional if DATABASE_URL provided)
        postgres_db: PostgreSQL database name (optional if DATABASE_URL provided)
        postgres_host: PostgreSQL host (optional if DATABASE_URL provided)
        postgres_port: PostgreSQL port (optional if DATABASE_URL provided)
        debug: Enable debug mode
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        secret_key: Secret key for JWT token signing
        api_v1_prefix: API version 1 URL prefix
        gemini_api_key: Google Gemini API key
        gemini_model: Gemini model name to use
        host: Server host address
        port: Server port number
    """

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


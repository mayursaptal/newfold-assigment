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
from pathlib import Path
from dotenv import load_dotenv

# Explicitly load .env file from current directory or /app (for Docker)
# Use override=True to ensure environment variables take precedence
env_paths = [Path(".env"), Path("/app/.env")]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path, override=True)
        break


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
        openai_api_key: OpenAI API key
        openai_model: OpenAI model name (e.g., gpt-4o, gpt-4, gpt-3.5-turbo)
        openai_org_id: OpenAI organization ID (optional)
        host: Server host address
        port: Server port number
    """

    # Database Configuration
    database_url: str = "postgresql+asyncpg://postgres:postgres@postgres:5432/interview_db"
    # Individual postgres fields are optional if DATABASE_URL is provided
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = None
    postgres_port: Optional[int] = None

    # Application Settings
    debug: bool = True
    log_level: str = "INFO"
    secret_key: str = "dev-secret-key-change-in-production"
    api_v1_prefix: str = "/api/v1"

    # AI Configuration (OpenAI)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_org_id: Optional[str] = None

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Global settings instance
settings = Settings()

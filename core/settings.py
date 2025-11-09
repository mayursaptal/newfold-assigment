"""Application settings using Pydantic BaseSettings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "interview_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    # Application Settings
    debug: bool = False
    log_level: str = "INFO"
    secret_key: str
    api_v1_prefix: str = "/api/v1"

    # Semantic Kernel / AI Configuration
    semantic_kernel_api_key: Optional[str] = None
    semantic_kernel_endpoint: str = "https://api.openai.com/v1"
    semantic_kernel_model: str = "gpt-4"

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


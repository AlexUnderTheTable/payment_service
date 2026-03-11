"""Application Configuration"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment"""

    # Database
    database_url: str

    # API Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True

    # Bank API
    bank_api_base_url: str = "https://bank.api"
    bank_api_timeout: int = 30
    bank_api_max_retries: int = 3
    bank_api_retry_delay: int = 1

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

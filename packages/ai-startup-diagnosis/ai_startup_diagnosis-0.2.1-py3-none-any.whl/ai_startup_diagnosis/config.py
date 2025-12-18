"""Application configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: Optional[str] = None

    # API Key Authentication
    api_keys: str = ""  # Comma-separated list of valid API keys

    # Rate Limiting Configuration
    rate_limit_per_hour: int = 100
    rate_limit_per_minute: int = 10

    # Application Configuration
    app_name: str = "AI Startup Diagnosis API"
    app_version: str = "0.1.0"
    debug: bool = False

    # CORS Configuration
    cors_origins: list[str] = ["*"]  # Allow all origins by default

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False

    def get_valid_api_keys(self) -> list[str]:
        """Get list of valid API keys from comma-separated string."""
        if not self.api_keys:
            return []
        return [key.strip() for key in self.api_keys.split(",") if key.strip()]


settings = Settings()


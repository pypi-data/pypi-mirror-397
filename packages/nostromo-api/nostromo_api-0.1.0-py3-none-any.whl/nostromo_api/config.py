"""
API Configuration using Pydantic Settings.
"""

import secrets
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="NOSTROMO_",
        env_file=".env",
        extra="ignore",
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Authentication
    secret_key: str = secrets.token_urlsafe(32)
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    api_keys: str = ""  # Comma-separated list of valid API keys

    # LLM Provider
    provider: str = "anthropic"
    model: str = "claude-3-5-haiku-latest"
    max_tokens: int = 4096
    temperature: float = 0.7

    # API Keys (from environment)
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # CORS
    cors_origins: str = "*"

    @property
    def valid_api_keys(self) -> set[str]:
        """Get set of valid API keys."""
        if not self.api_keys:
            return set()
        return {k.strip() for k in self.api_keys.split(",") if k.strip()}

    @property
    def cors_origin_list(self) -> list[str]:
        """Get list of CORS origins."""
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]

    def get_llm_api_key(self) -> str:
        """Get the API key for the configured provider."""
        if self.provider == "anthropic":
            return self.anthropic_api_key
        elif self.provider == "openai":
            return self.openai_api_key
        return ""


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

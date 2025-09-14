"""
Configuration management for the Grok chatbot back‑end.

Settings are loaded from environment variables via ``pydantic.BaseSettings``.
When developing locally you can copy ``.env.example`` to ``.env`` in the
``backend`` directory to set values such as ``GROK_API_KEY`` and
``GROK_MODEL``.  All values have sensible defaults except the API key.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # xAI Grok API
    grok_api_key: Optional[str] = Field(None, env="GROK_API_KEY")
    grok_model: str = Field("grok-2-latest", env="GROK_MODEL")

    # Server configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    allowed_origins: str = Field("http://localhost:5173", env="ALLOWED_ORIGINS")
    log_level: str = Field("info", env="LOG_LEVEL")

    # Optional system prompt injected at the start of every conversation
    system_prompt: Optional[str] = Field(None, env="SYSTEM_PROMPT")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()

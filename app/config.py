"""
AgentFlow Configuration Module
Centralizes all environment-based settings using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ─── App ─────────────────────────────────────────────
    APP_NAME: str = "AgentFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ─── Database ────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./agentflow.db"

    # ─── Redis ───────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"

    # ─── Auth ────────────────────────────────────────────
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ─── AI APIs ─────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # ─── Integrations ────────────────────────────────────
    GMAIL_API_KEY: str = ""
    JIRA_SERVER: str = ""
    JIRA_EMAIL: str = ""
    JIRA_API_TOKEN: str = ""
    SLACK_BOT_TOKEN: str = ""

    # ─── Celery ──────────────────────────────────────────
    CELERY_BROKER: Optional[str] = None
    CELERY_BACKEND: Optional[str] = None

    # ─── Logging ─────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # ─── Features ────────────────────────────────────────
    ENABLE_WEBHOOKS: bool = True
    ENABLE_MONITORING: bool = True

    @property
    def celery_broker_url(self) -> str:
        return self.CELERY_BROKER or self.REDIS_URL

    @property
    def celery_backend_url(self) -> str:
        return self.CELERY_BACKEND or self.REDIS_URL

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()


settings = get_settings()

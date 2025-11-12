"""
Example Pydantic configuration schema for testing env-integrity-check.
"""

from pydantic import BaseModel, Field
from typing import Optional


class Settings(BaseModel):
    """Application configuration schema."""

    # Database settings
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string",
        min_length=1
    )

    DATABASE_POOL_SIZE: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size"
    )

    # API settings
    API_KEY: str = Field(
        ...,
        description="Secret API key for external service",
        min_length=32
    )

    API_TIMEOUT: int = Field(
        default=30,
        ge=1,
        description="API timeout in seconds"
    )

    # Application settings
    APP_NAME: str = Field(
        default="MyApp",
        description="Application name"
    )

    DEBUG: bool = Field(
        default=False,
        description="Enable debug mode"
    )

    LOG_LEVEL: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="Logging level"
    )

    # Optional settings
    SENTRY_DSN: Optional[str] = Field(
        default=None,
        description="Sentry DSN for error tracking"
    )

    REDIS_URL: Optional[str] = Field(
        default=None,
        description="Redis connection string for caching"
    )

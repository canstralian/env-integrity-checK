"""Example Pydantic schema for environment validation."""

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration schema."""

    app_name: str = Field(..., description="Application name")
    app_env: str = Field(..., description="Application environment (development, production, etc.)")
    database_url: str = Field(..., description="Database connection URL")
    api_key: str = Field(..., description="API key for external services")
    debug: bool = Field(default=False, description="Debug mode")
    port: int = Field(default=8000, description="Application port")

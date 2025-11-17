from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """
    Centralized application settings loaded from environment.

    Environment variables:
    - DATABASE_URL: Async SQLAlchemy URL for PostgreSQL (e.g., postgresql+asyncpg://user:pass@host:5432/db)
    - JWT_SECRET: Secret used for signing JWTs (stub for now)
    - CORS_ALLOWED_ORIGINS: Comma-separated origins. Default allows http://localhost:3000 for dev.
    - ENABLE_MIGRATIONS: 'true' or 'false' to run migrations on startup (placeholder switch)
    """

    # Database
    DATABASE_URL: str = Field(default="", description="SQLAlchemy async URL for PostgreSQL via asyncpg")

    # Security
    JWT_SECRET: str = Field(default="dev-secret", description="JWT secret (development default)")

    # CORS
    CORS_ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins",
    )

    # Feature flags
    ENABLE_MIGRATIONS: bool = Field(default=False, description="Run migrations on startup")

    # Derived helpers
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


# PUBLIC_INTERFACE
@lru_cache
def get_settings() -> AppSettings:
    """Return cached application settings instance loaded from environment."""
    return AppSettings()

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
    - ALLOWED_ORIGINS: Legacy comma-separated origins (fallback support).
    - FRONTEND_URL: Single origin for the frontend (e.g., https://host:3000)
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
    # Legacy / compatibility variable support
    ALLOWED_ORIGINS: str = Field(
        default="",
        description="Legacy comma-separated list of allowed origins (fallback).",
    )
    # Convenience for single-origin setups
    FRONTEND_URL: str = Field(
        default="",
        description="Public origin of the frontend (e.g., https://example.com:3000).",
    )

    # Feature flags
    ENABLE_MIGRATIONS: bool = Field(default=False, description="Run migrations on startup")

    # Derived helpers
    def cors_origins_list(self) -> List[str]:
        """
        Build a unique, normalized list of allowed origins by combining:
        - CORS_ALLOWED_ORIGINS (preferred)
        - ALLOWED_ORIGINS (legacy fallback)
        - FRONTEND_URL (single value convenience)
        """
        raw_lists: List[str] = [
            self.CORS_ALLOWED_ORIGINS or "",
            self.ALLOWED_ORIGINS or "",
            self.FRONTEND_URL or "",
        ]

        items: List[str] = []
        seen = set()
        for raw in raw_lists:
            if not raw:
                continue
            parts = [p.strip() for p in raw.split(",") if p.strip()]
            for p in parts:
                # Normalize: strip trailing slash if present
                norm = p[:-1] if p.endswith("/") else p
                if norm not in seen:
                    seen.add(norm)
                    items.append(norm)
        return items

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

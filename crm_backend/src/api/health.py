from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.core.db import check_db_connection

router = APIRouter(tags=["Health"])


class HealthStatus(BaseModel):
    status: str = Field(..., description="Overall status: ok|degraded|down")
    db: str = Field(..., description="Database status: up|down")
    version: str = Field(..., description="Application version")


# PUBLIC_INTERFACE
@router.get("/", summary="Health Check")
async def health_root() -> HealthStatus:
    """Basic health endpoint at '/'. Includes DB status probe."""
    db_ok = await check_db_connection()
    overall = "ok" if db_ok else "degraded"
    # Version is provided by the main app metadata; for simplicity, keep a static string here.
    return HealthStatus(status=overall, db="up" if db_ok else "down", version="1.0.0")


# PUBLIC_INTERFACE
@router.get("/ready", summary="Readiness Check")
async def readiness() -> HealthStatus:
    """Readiness endpoint at '/ready' that requires DB connectivity."""
    db_ok = await check_db_connection()
    overall = "ok" if db_ok else "down"
    return HealthStatus(status=overall, db="up" if db_ok else "down", version="1.0.0")

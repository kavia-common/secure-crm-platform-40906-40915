import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Attempt to load .env if present; not required for container runtime
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    # Running without python-dotenv or .env file is fine
    pass


# PUBLIC_INTERFACE
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance with metadata,
        CORS middleware, and basic routes registered.
    """
    tags_metadata = [
        {
            "name": "Health",
            "description": "Endpoints for liveness/readiness health checks.",
        },
        {
            "name": "Docs",
            "description": "Developer documentation helpers and service usage info.",
        },
    ]

    app = FastAPI(
        title="CRM Backend API",
        description=(
            "FastAPI backend providing RESTful APIs and integration points for the CRM platform. "
            "This minimal bootstrap exposes health checks and is designed to connect to the "
            "PostgreSQL database via environment variables only (no file path coupling)."
        ),
        version="0.1.0",
        openapi_tags=tags_metadata,
    )

    # Allow CORS by default for development; tighten in production as needed
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_routes(app)
    return app


class HealthResponse(BaseModel):
    """Structured response model for health endpoint."""

    status: str = Field(..., description="Service status; 'ok' indicates healthy.")
    service: str = Field(..., description="Service identifier.")
    time_utc: str = Field(..., description="Current server time in UTC ISO 8601 format.")
    db_configured: bool = Field(
        ..., description="True if required DB environment variables are defined."
    )
    db_host: Optional[str] = Field(
        None, description="Database host value when configured."
    )


def _db_env_configured() -> tuple[bool, Optional[str]]:
    """Check if DB environment variables are present (host and name are minimum signals)."""
    db_host = os.getenv("CRM_DB_HOST") or os.getenv("DB_HOST")
    db_name = os.getenv("CRM_DB_NAME") or os.getenv("DB_NAME")
    # user/password/port are optional for this simple readiness signal
    configured = bool(db_host) and bool(db_name)
    return configured, db_host


def register_routes(app: FastAPI) -> None:
    """Register HTTP routes on the provided FastAPI application instance."""
    # PUBLIC_INTERFACE
    @app.get(
        "/",
        tags=["Health"],
        summary="Root service status",
        description="Returns basic status for the CRM Backend service.",
        response_model=HealthResponse,
    )
    def root() -> HealthResponse:
        """Root route returning a simple health-like payload."""
        configured, db_host = _db_env_configured()
        return HealthResponse(
            status="ok",
            service="crm_backend",
            time_utc=datetime.now(timezone.utc).isoformat(),
            db_configured=configured,
            db_host=db_host,
        )

    # PUBLIC_INTERFACE
    @app.get(
        "/health",
        tags=["Health"],
        summary="Liveness/Readiness probe",
        description=(
            "Indicates if the service is alive and can accept traffic. "
            "Database configuration is reported based on environment variables, "
            "but no connection is established in this minimal scaffold."
        ),
        response_model=HealthResponse,
        operation_id="getHealth",
    )
    def health() -> HealthResponse:
        """Health endpoint suitable for container orchestration probes."""
        configured, db_host = _db_env_configured()
        return HealthResponse(
            status="ok",
            service="crm_backend",
            time_utc=datetime.now(timezone.utc).isoformat(),
            db_configured=configured,
            db_host=db_host,
        )

    # PUBLIC_INTERFACE
    @app.get(
        "/ws/help",
        tags=["Docs"],
        summary="WebSocket usage info",
        description=(
            "Provides guidance for real-time connections. "
            "Note: WebSocket endpoints are not yet implemented in this scaffold."
        ),
        operation_id="getWebSocketHelp",
    )
    def websocket_help() -> dict:
        """Return WebSocket usage guidance and current status."""
        return {
            "websocket_enabled": False,
            "message": "No WebSocket endpoints are currently implemented. "
            "Future versions will provide real-time updates via /ws/* routes.",
        }


# Create the application instance for the ASGI server entrypoint
app = create_app()

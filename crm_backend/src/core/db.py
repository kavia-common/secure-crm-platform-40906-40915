from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from src.core.settings import get_settings

_engine: Optional[AsyncEngine] = None
_sessionmaker_cached: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine() -> AsyncEngine:
    """
    Create (once) and return the global AsyncEngine based on settings.DATABASE_URL.
    Raises ValueError if DATABASE_URL is missing.
    """
    global _engine
    settings = get_settings()
    if not settings.DATABASE_URL:
        raise ValueError("DATABASE_URL is not configured. Please set it in environment.")
    if _engine is None:
        _engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=5, max_overflow=10)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the async session factory, initializing the engine if needed."""
    global _sessionmaker_cached
    if _sessionmaker_cached is None:
        eng = get_engine()
        _sessionmaker_cached = async_sessionmaker(bind=eng, autoflush=False, expire_on_commit=False)
    return _sessionmaker_cached


# PUBLIC_INTERFACE
@asynccontextmanager
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession with proper cleanup."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        await session.close()


# PUBLIC_INTERFACE
async def check_db_connection(timeout_seconds: float = 5.0) -> bool:
    """
    Try a lightweight SELECT 1 to verify DB connectivity.
    Returns True on success, False if timed out or any error occurs.
    """
    try:
        async def _probe() -> bool:
            eng = get_engine()
            async with eng.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True

        return await asyncio.wait_for(_probe(), timeout=timeout_seconds)
    except Exception:
        return False

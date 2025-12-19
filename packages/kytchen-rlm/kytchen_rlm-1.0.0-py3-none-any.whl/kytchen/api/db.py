"""SQLAlchemy async database setup for Kytchen Cloud.

This module configures PostgreSQL connectivity using asyncpg and provides
a session factory for dependency injection in FastAPI endpoints.

In dev mode (KYTCHEN_DEV_MODE=1), uses SQLite for easy testing.
"""

from __future__ import annotations

import json
import os
import uuid as uuid_module
from typing import Any, AsyncGenerator, List

try:
    from sqlalchemy import TypeDecorator, String, Text
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.orm import DeclarativeBase
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY as PG_ARRAY
    SQLALCHEMY_AVAILABLE = True
except Exception:  # pragma: no cover
    AsyncSession = Any  # type: ignore[assignment]
    async_sessionmaker = None  # type: ignore[assignment]
    create_async_engine = None  # type: ignore[assignment]
    TypeDecorator = Any  # type: ignore[assignment]
    SQLALCHEMY_AVAILABLE = False

    class DeclarativeBase:  # type: ignore[no-redef]
        pass


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# -----------------------------------------------------------------------------
# Cross-Database Compatible Types
# -----------------------------------------------------------------------------

if SQLALCHEMY_AVAILABLE:
    class GUID(TypeDecorator):
        """Cross-database UUID type.

        Uses PostgreSQL's native UUID type when available, falls back to
        CHAR(36) for SQLite and other databases.
        """
        impl = String(36)
        cache_ok = True

        def load_dialect_impl(self, dialect):
            if dialect.name == "postgresql":
                return dialect.type_descriptor(PG_UUID(as_uuid=True))
            return dialect.type_descriptor(String(36))

        def process_bind_param(self, value, dialect):
            if value is None:
                return value
            if dialect.name == "postgresql":
                return value
            # For SQLite/other: convert UUID to string
            if isinstance(value, uuid_module.UUID):
                return str(value)
            return str(uuid_module.UUID(value))

        def process_result_value(self, value, dialect):
            if value is None:
                return value
            if isinstance(value, uuid_module.UUID):
                return value
            return uuid_module.UUID(value)


    class UUIDArray(TypeDecorator):
        """Cross-database UUID array type.

        Uses PostgreSQL's native ARRAY(UUID) when available, falls back to
        JSON-encoded string for SQLite and other databases.
        """
        impl = Text
        cache_ok = True

        def load_dialect_impl(self, dialect):
            if dialect.name == "postgresql":
                return dialect.type_descriptor(PG_ARRAY(PG_UUID(as_uuid=True)))
            return dialect.type_descriptor(Text())

        def process_bind_param(self, value, dialect):
            if value is None:
                return [] if dialect.name != "postgresql" else None
            if dialect.name == "postgresql":
                return value
            # For SQLite/other: convert list of UUIDs to JSON string
            return json.dumps([str(v) if isinstance(v, uuid_module.UUID) else v for v in value])

        def process_result_value(self, value, dialect):
            if value is None:
                return []
            if dialect.name == "postgresql":
                return value if value else []
            # For SQLite/other: parse JSON string back to list of UUIDs
            if isinstance(value, str):
                items = json.loads(value) if value else []
                return [uuid_module.UUID(v) if isinstance(v, str) else v for v in items]
            return value if value else []
else:
    # Stubs for when SQLAlchemy is not available
    GUID = Any  # type: ignore[assignment]
    UUIDArray = Any  # type: ignore[assignment]


def is_dev_mode() -> bool:
    """Check if running in development mode."""
    return os.getenv("KYTCHEN_DEV_MODE", "0").strip() in ("1", "true", "yes")


def get_database_url() -> str:
    """Get database connection URL from environment.

    In dev mode, uses SQLite for easy testing.
    In production, uses DATABASE_URL or falls back to individual components.

    Returns:
        Async database connection URL
    """
    # Dev mode: use SQLite
    if is_dev_mode():
        return "sqlite+aiosqlite:///:memory:"

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # SQLAlchemy async engine expects postgresql+asyncpg://
        if database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        return database_url

    # Fallback for local development with Postgres
    user = os.getenv("POSTGRES_USER", "kytchen")
    password = os.getenv("POSTGRES_PASSWORD", "kytchen")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "kytchen")

    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"


# Lazily initialized engine and session factory
_engine = None
_AsyncSessionLocal = None


def _get_engine():
    """Get or create the database engine (lazy initialization)."""
    global _engine
    if _engine is None and create_async_engine is not None:
        url = get_database_url()
        if url.startswith("sqlite"):
            # SQLite doesn't support pool_pre_ping, pool_size, max_overflow
            _engine = create_async_engine(
                url,
                echo=os.getenv("KYTCHEN_SQL_ECHO", "false").lower() in ("true", "1"),
            )
        else:
            _engine = create_async_engine(
                url,
                echo=os.getenv("KYTCHEN_SQL_ECHO", "false").lower() in ("true", "1"),
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
    return _engine


def _get_session_local():
    """Get or create the session factory (lazy initialization)."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        eng = _get_engine()
        if async_sessionmaker is not None and eng is not None:
            _AsyncSessionLocal = async_sessionmaker(
                eng,
                class_=AsyncSession,
                expire_on_commit=False,
                autocommit=False,
                autoflush=False,
            )
    return _AsyncSessionLocal


# Property-like access for backwards compatibility
# These are accessed as `db.engine` and `db.AsyncSessionLocal`
class _EngineProxy:
    """Lazy proxy for engine to maintain backwards compatibility."""
    def __getattr__(self, name):
        return getattr(_get_engine(), name)

    def __bool__(self):
        return _get_engine() is not None


class _SessionLocalProxy:
    """Lazy proxy for session factory to maintain backwards compatibility."""
    def __call__(self):
        factory = _get_session_local()
        if factory is None:
            raise RuntimeError("Database not initialized")
        return factory()

    def __bool__(self):
        return _get_session_local() is not None


engine = _EngineProxy()
AsyncSessionLocal = _SessionLocalProxy()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for database sessions.

    Usage:
        @app.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Model))
            return result.scalars().all()

    Yields:
        AsyncSession: Database session that auto-commits/rolls back
    """
    session_factory = _get_session_local()
    if session_factory is None:
        # Dev-mode friendly: allow importing/running API scaffolding tests without
        # SQLAlchemy installed. Production mode requires installing `kytchen[api]`.
        yield None  # type: ignore[misc]
        return

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database tables.

    Creates all tables defined in models.py. This should only be run
    in development. Production should use Alembic migrations.
    """
    # Import models to ensure they're registered with Base.metadata
    from . import models  # noqa: F401

    eng = _get_engine()
    if eng is None:
        raise RuntimeError("SQLAlchemy is required for database mode. Install `pip install 'kytchen[api]'`.")

    async with eng.begin() as conn:
        # Create pgcrypto extension for PostgreSQL (skip for SQLite)
        if not is_dev_mode():
            from sqlalchemy import text
            await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pgcrypto"'))
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database engine and cleanup connections.

    Call this during application shutdown.
    """
    eng = _get_engine()
    if eng is None:
        return
    await eng.dispose()

"""Auth dependencies for Kytchen Cloud.

Supports two authentication modes:
1. Dashboard auth via Replit OIDC (handled by Auth.js in frontend)
2. MCP auth via Bearer `kyt_sk_...` API keys (for programmatic access)

This module implements:
- MCP API-key parsing and validation
- Database lookup for API key -> workspace mapping
- Dev-only key resolver that doesn't require database
"""

from __future__ import annotations

import hashlib
import os
import uuid
from dataclasses import dataclass

from typing import Any

try:
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
except Exception:  # pragma: no cover
    select = None  # type: ignore[assignment]
    AsyncSession = Any  # type: ignore[assignment]

from .limits import PlanLimits, get_plan_limits


@dataclass(slots=True)
class WorkspaceAuth:
    api_key: str
    workspace_id: str
    plan: str = "free"
    api_key_id: str | None = None

    @property
    def limits(self) -> PlanLimits:
        return get_plan_limits(self.plan)


def require_bearer_api_key(authorization: str | None) -> str:
    """Extract and validate API key from Authorization header.

    Args:
        authorization: Authorization header value

    Returns:
        API key string (kyt_sk_...)

    Raises:
        ValueError: If header is missing or invalid
    """
    if not authorization:
        raise ValueError("Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise ValueError("Authorization must be Bearer <key>")
    key = authorization.split(None, 1)[1].strip()
    if not key.startswith("kyt_sk_"):
        raise ValueError("Invalid KYTCHEN_API_KEY (expected prefix kyt_sk_)")
    return key


def hash_api_key(api_key: str) -> str:
    """Hash API key for database storage.

    Args:
        api_key: Plain-text API key

    Returns:
        SHA256 hash (hex)
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


async def resolve_workspace(api_key: str, db: AsyncSession) -> WorkspaceAuth:
    """Resolve workspace from API key (database lookup).

    Args:
        api_key: Plain-text API key
        db: Database session

    Returns:
        WorkspaceAuth with workspace_id and plan

    Raises:
        ValueError: If API key is invalid or revoked
    """
    if select is None:
        raise RuntimeError("SQLAlchemy is required for database-backed auth. Install `pip install 'kytchen[api]'`.")

    from .models import APIKey, Workspace

    key_hash = hash_api_key(api_key)

    # Look up API key in database
    result = await db.execute(
        select(APIKey, Workspace)
        .join(Workspace, APIKey.workspace_id == Workspace.id)
        .where(APIKey.key_hash == key_hash)
    )
    row = result.first()

    if row is None:
        raise ValueError("Invalid API key")

    api_key_obj, workspace = row

    # Check if revoked
    if api_key_obj.revoked_at is not None:
        raise ValueError("API key has been revoked")

    # Update last_used_at (fire-and-forget, don't wait for commit)
    from datetime import datetime, timezone
    from sqlalchemy import update

    await db.execute(
        update(APIKey)
        .where(APIKey.id == api_key_obj.id)
        .values(last_used_at=datetime.now(timezone.utc))
    )

    return WorkspaceAuth(
        api_key=api_key,
        workspace_id=str(workspace.id),
        plan=workspace.plan.value,
        api_key_id=str(api_key_obj.id),
    )


# -----------------------------------------------------------------------------
# Development-only helpers (no database required)
# -----------------------------------------------------------------------------


def dev_workspace_id_from_key(api_key: str) -> str:
    """Generate deterministic workspace ID from API key (dev only).

    Args:
        api_key: API key

    Returns:
        UUID string
    """
    return str(uuid.uuid5(uuid.NAMESPACE_URL, api_key))


def dev_resolve_workspace(api_key: str) -> WorkspaceAuth:
    """Resolve workspace without database (dev only).

    Args:
        api_key: API key

    Returns:
        WorkspaceAuth with generated workspace_id
    """
    plan = os.getenv("KYTCHEN_DEV_PLAN", "free").strip().lower() or "free"
    return WorkspaceAuth(
        api_key=api_key,
        workspace_id=dev_workspace_id_from_key(api_key),
        plan=plan,
    )


"""Authentication verification routes."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import WorkspaceAuth, dev_resolve_workspace, require_bearer_api_key, resolve_workspace
from ..db import get_db

router = APIRouter(prefix="/v1/auth", tags=["auth"])


def is_dev_mode() -> bool:
    """Check if running in development mode."""
    return os.getenv("KYTCHEN_DEV_MODE", "0").strip() in ("1", "true", "yes")


async def get_auth(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceAuth:
    """FastAPI dependency for authentication."""
    try:
        api_key = require_bearer_api_key(authorization)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    if is_dev_mode():
        return dev_resolve_workspace(api_key)

    try:
        return await resolve_workspace(api_key, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.get("/whoami")
async def whoami(
    auth: WorkspaceAuth = Depends(get_auth),
) -> dict[str, Any]:
    """Verify authentication and return workspace info."""
    return {
        "authenticated": True,
        "workspace": {
            "id": auth.workspace_id,
            "plan": auth.plan,
        },
        "scopes": ["api"],  # Future proofing
    }

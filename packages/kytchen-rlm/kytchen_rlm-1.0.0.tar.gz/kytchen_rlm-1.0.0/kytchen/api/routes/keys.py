"""API key management routes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import WorkspaceAuth, get_auth
from ..db import get_db
from ..models import APIKey

router = APIRouter(prefix="/v1/keys", tags=["keys"])


@router.delete("/{key_id}")
async def revoke_key(
    key_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Revoke an API key."""
    import uuid as uuid_module

    conditions = [APIKey.key_prefix == key_id]

    try:
        uuid_val = uuid_module.UUID(key_id)
        conditions.append(APIKey.id == uuid_val)
    except ValueError:
        pass

    stmt = select(APIKey).where(
        APIKey.workspace_id == auth.workspace_id,
        or_(*conditions)
    )

    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()

    if not api_key:
        # Try to search by full key if it looks like one?
        # If it is a full key, we can hash it and look it up.
        from ..auth import hash_api_key
        key_hash = hash_api_key(key_id)
        stmt = select(APIKey).where(
            APIKey.workspace_id == auth.workspace_id,
            APIKey.key_hash == key_hash
        )
        result = await db.execute(stmt)
        api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    if api_key.revoked_at:
        return {"revoked": True, "already_revoked": True}

    # Revoke it
    api_key.revoked_at = datetime.now(timezone.utc)
    await db.commit()

    return {"revoked": True, "key_id": str(api_key.id), "prefix": api_key.key_prefix}

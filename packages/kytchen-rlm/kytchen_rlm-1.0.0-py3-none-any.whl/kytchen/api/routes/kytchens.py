"""Kytchen API routes (SHA-107: Menu API, SHA-108: Kytchen Model).

This module implements:
- Kytchen CRUD: List, Create, Get, Update, Delete
- Menu API: GET /v1/kytchens/{id}/menu (OpenAI-compatible tool schema)
- Pantry: GET/POST /v1/kytchens/{id}/pantry
- Tickets: POST /v1/kytchens/{id}/tickets (fire queries)

"GitHub is where code sleeps. Kytchen is where code cooks."
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..auth import WorkspaceAuth, dev_resolve_workspace, require_bearer_api_key, resolve_workspace
from ..db import get_db
from ..models import (
    Dataset,
    Kytchen,
    KytchenDataset,
    KytchenVisibility,
    Member,
    MemberRole,
    User,
)


def is_dev_mode() -> bool:
    """Check if running in development mode."""
    return os.getenv("KYTCHEN_DEV_MODE", "0").strip() in ("1", "true", "yes")


async def get_auth(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceAuth:
    """FastAPI dependency for authentication in kytchen routes."""
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


from ..schemas.kytchen import (
    KytchenCreate,
    KytchenListResponse,
    KytchenResponse,
    KytchenUpdate,
)
from ..schemas.menu import (
    DEFAULT_TOOLS,
    BudgetDefaults,
    DatasetInfo,
    Endpoints,
    KytchenMeta,
    MenuResponse,
    PantryStatus,
    ToolDefinition,
)
from ..schemas.ticket import (
    TicketCreate,
    TicketListResponse,
    TicketMetrics,
    TicketResponse,
)

router = APIRouter(prefix="/v1/kytchens", tags=["kytchens"])


# Re-export get_auth for use by the main app
__all__ = ["router", "get_auth"]


# Re-export get_auth for use by the main app



def _slugify(name: str) -> str:
    """Convert name to URL-friendly slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:255].strip("-")


def _format_kitchen_id(uuid: UUID) -> str:
    """Format UUID as Kytchen ID (kyt_...)."""
    return f"kyt_{str(uuid).replace('-', '')[:12]}"


def _get_base_url() -> str:
    """Get the API base URL from environment or default."""
    return os.getenv("KYTCHEN_API_URL", "https://api.kytchen.dev")


# -----------------------------------------------------------------------------
# Kytchen CRUD
# -----------------------------------------------------------------------------


@router.get("", response_model=KytchenListResponse)
async def list_kytchens(
    limit: int = 50,
    offset: int = 0,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> KytchenListResponse:
    """List all Kytchens in the workspace."""
    # Count total
    count_query = select(func.count(Kytchen.id)).where(
        Kytchen.workspace_id == auth.workspace_id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Fetch kytchens with pantry stats
    query = (
        select(Kytchen)
        .options(selectinload(Kytchen.pantry_items).selectinload(KytchenDataset.dataset))
        .where(Kytchen.workspace_id == auth.workspace_id)
        .order_by(Kytchen.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    kytchens = result.scalars().all()

    return KytchenListResponse(
        kytchens=[
            KytchenResponse(
                id=_format_kitchen_id(k.id),
                slug=k.slug,
                name=k.name,
                description=k.description,
                visibility=k.visibility.value,
                forked_from=_format_kitchen_id(k.forked_from_id) if k.forked_from_id else None,
                created_at=k.created_at,
                updated_at=k.updated_at,
                dataset_count=len(k.pantry_items),
                total_size_bytes=sum(
                    item.dataset.size_bytes for item in k.pantry_items if item.dataset
                ),
            )
            for k in kytchens
        ],
        total=total,
        has_more=offset + len(kytchens) < total,
    )


@router.post("", response_model=KytchenResponse, status_code=201)
async def create_kytchen(
    body: KytchenCreate,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> KytchenResponse:
    """Create a new Kytchen."""
    slug = body.slug or _slugify(body.name)

    # Check for duplicate slug
    existing = await db.execute(
        select(Kytchen).where(
            Kytchen.workspace_id == auth.workspace_id,
            Kytchen.slug == slug,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"Kytchen with slug '{slug}' already exists")

    # Handle forking
    forked_from_id = None
    if body.fork_from:
        # Parse fork_from ID
        fork_uuid = body.fork_from.replace("kyt_", "")
        # Find the source kytchen (must be public or in same workspace)
        fork_query = select(Kytchen).where(
            Kytchen.id == fork_uuid,
        )
        fork_result = await db.execute(fork_query)
        source_kytchen = fork_result.scalar_one_or_none()
        if not source_kytchen:
            raise HTTPException(status_code=404, detail="Source kytchen not found")
        if (
            source_kytchen.visibility == KytchenVisibility.private
            and source_kytchen.workspace_id != auth.workspace_id
        ):
            raise HTTPException(status_code=403, detail="Cannot fork private kytchen")
        forked_from_id = source_kytchen.id

    kytchen = Kytchen(
        workspace_id=auth.workspace_id,
        slug=slug,
        name=body.name,
        description=body.description,
        visibility=KytchenVisibility(body.visibility),
        forked_from_id=forked_from_id,
        budget_defaults={
            "max_tokens": 50000,
            "max_cost_usd": 1.0,
            "max_iterations": 20,
            "timeout_seconds": 120,
        },
        custom_tools=[],
    )
    db.add(kytchen)
    await db.commit()
    await db.refresh(kytchen)

    return KytchenResponse(
        id=_format_kitchen_id(kytchen.id),
        slug=kytchen.slug,
        name=kytchen.name,
        description=kytchen.description,
        visibility=kytchen.visibility.value,
        forked_from=_format_kitchen_id(forked_from_id) if forked_from_id else None,
        created_at=kytchen.created_at,
        updated_at=kytchen.updated_at,
        dataset_count=0,
        total_size_bytes=0,
    )


@router.get("/{kytchen_id}", response_model=KytchenResponse)
async def get_kytchen(
    kytchen_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> KytchenResponse:
    """Get a Kytchen by ID or slug."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db)

    return KytchenResponse(
        id=_format_kitchen_id(kytchen.id),
        slug=kytchen.slug,
        name=kytchen.name,
        description=kytchen.description,
        visibility=kytchen.visibility.value,
        forked_from=_format_kitchen_id(kytchen.forked_from_id) if kytchen.forked_from_id else None,
        created_at=kytchen.created_at,
        updated_at=kytchen.updated_at,
        dataset_count=len(kytchen.pantry_items),
        total_size_bytes=sum(
            item.dataset.size_bytes for item in kytchen.pantry_items if item.dataset
        ),
    )


@router.patch("/{kytchen_id}", response_model=KytchenResponse)
async def update_kytchen(
    kytchen_id: str,
    body: KytchenUpdate,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> KytchenResponse:
    """Update a Kytchen."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db, require_owner=True)

    if body.name is not None:
        kytchen.name = body.name
    if body.description is not None:
        kytchen.description = body.description
    if body.visibility is not None:
        kytchen.visibility = KytchenVisibility(body.visibility)

    await db.commit()
    await db.refresh(kytchen)

    return KytchenResponse(
        id=_format_kitchen_id(kytchen.id),
        slug=kytchen.slug,
        name=kytchen.name,
        description=kytchen.description,
        visibility=kytchen.visibility.value,
        forked_from=_format_kitchen_id(kytchen.forked_from_id) if kytchen.forked_from_id else None,
        created_at=kytchen.created_at,
        updated_at=kytchen.updated_at,
        dataset_count=len(kytchen.pantry_items),
        total_size_bytes=sum(
            item.dataset.size_bytes for item in kytchen.pantry_items if item.dataset
        ),
    )


@router.delete("/{kytchen_id}", status_code=204)
async def delete_kytchen(
    kytchen_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete (86) a Kytchen."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db, require_owner=True)
    await db.delete(kytchen)
    await db.commit()


# -----------------------------------------------------------------------------
# Menu API (SHA-107) - The main event
# -----------------------------------------------------------------------------


@router.get("/{kytchen_id}/menu", response_model=MenuResponse)
async def get_menu(
    kytchen_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> MenuResponse:
    """Get the Menu (OpenAI-compatible tool schema) for a Kytchen.

    This is how agents know what's for dinner. The response includes:
    - Kytchen metadata
    - Pantry status (available datasets)
    - Tools in OpenAI function format
    - API endpoints

    Any agent (Cursor, Windsurf, AutoGen, CrewAI) can use this
    to plug into Kytchen without custom code.
    """
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db, allow_public=True)
    base_url = _get_base_url()
    kytchen_id_str = _format_kitchen_id(kytchen.id)

    # Build pantry status
    datasets: list[DatasetInfo] = []
    total_size = 0
    total_tokens = 0
    latest_indexed: datetime | None = None

    for item in kytchen.pantry_items:
        ds = item.dataset
        if ds:
            size_tokens = ds.size_bytes // 4  # Rough estimate
            datasets.append(
                DatasetInfo(
                    id=str(ds.id),
                    name=ds.name,
                    format=_infer_format(ds.mime_type),
                    size_bytes=ds.size_bytes,
                    size_tokens_estimate=size_tokens,
                    indexed=item.indexed,
                    content_hash=ds.content_hash,
                )
            )
            total_size += ds.size_bytes
            total_tokens += size_tokens
            if item.indexed_at and (latest_indexed is None or item.indexed_at > latest_indexed):
                latest_indexed = item.indexed_at

    pantry = PantryStatus(
        datasets=datasets,
        total_size_bytes=total_size,
        total_tokens_estimate=total_tokens,
        indexed_at=latest_indexed,
    )

    # Build tools list: defaults + custom
    tools: list[ToolDefinition] = list(DEFAULT_TOOLS)
    for custom_tool in kytchen.custom_tools or []:
        try:
            tools.append(ToolDefinition.model_validate(custom_tool))
        except Exception:
            pass  # Skip invalid custom tools

    # Build budget defaults
    budget = BudgetDefaults.model_validate(kytchen.budget_defaults or {})

    # Build endpoints
    endpoints = Endpoints(
        menu=f"{base_url}/v1/kytchens/{kytchen_id_str}/menu",
        query=f"{base_url}/v1/kytchens/{kytchen_id_str}/tickets",
        stream=f"{base_url}/v1/kytchens/{kytchen_id_str}/tickets/stream",
        pantry=f"{base_url}/v1/kytchens/{kytchen_id_str}/pantry",
    )

    # Get chef handle from workspace owner
    chef_handle = None
    chef_query = (
        select(User)
        .join(Member, Member.user_id == User.id)
        .where(
            Member.workspace_id == kytchen.workspace_id,
            Member.role == MemberRole.owner,
        )
        .limit(1)
    )
    chef_result = await db.execute(chef_query)
    chef_user = chef_result.scalar_one_or_none()

    if chef_user and chef_user.replit_id:
        chef_handle = f"@{chef_user.replit_id}"
    elif chef_user and chef_user.name:
        # Fallback to name if replit_id is missing
        chef_handle = chef_user.name

    return MenuResponse(
        version="1.0.0",
        kytchen=KytchenMeta(
            id=kytchen_id_str,
            name=kytchen.name,
            description=kytchen.description,
            chef=chef_handle,
            visibility=kytchen.visibility.value,
            forked_from=_format_kitchen_id(kytchen.forked_from_id) if kytchen.forked_from_id else None,
            created_at=kytchen.created_at,
        ),
        pantry=pantry,
        tools=tools,
        budget_defaults=budget,
        endpoints=endpoints,
    )


# -----------------------------------------------------------------------------
# Pantry Management
# -----------------------------------------------------------------------------


@router.get("/{kytchen_id}/pantry")
async def get_pantry(
    kytchen_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get Pantry status for a Kytchen."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db)

    datasets = []
    for item in kytchen.pantry_items:
        ds = item.dataset
        if ds:
            datasets.append({
                "id": str(ds.id),
                "name": ds.name,
                "size_bytes": ds.size_bytes,
                "content_hash": ds.content_hash,
                "indexed": item.indexed,
                "indexed_at": item.indexed_at.isoformat() if item.indexed_at else None,
                "added_at": item.added_at.isoformat(),
            })

    return {
        "kytchen_id": _format_kitchen_id(kytchen.id),
        "datasets": datasets,
        "total_count": len(datasets),
        "total_size_bytes": sum(d["size_bytes"] for d in datasets),
    }


@router.post("/{kytchen_id}/pantry")
async def add_to_pantry(
    kytchen_id: str,
    body: dict[str, Any],
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Add a dataset to the Kytchen's Pantry."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db, require_owner=True)

    dataset_id = body.get("dataset_id")
    if not dataset_id:
        raise HTTPException(status_code=400, detail="Missing dataset_id")

    # Verify dataset exists and belongs to workspace
    dataset_query = select(Dataset).where(
        Dataset.id == dataset_id,
        Dataset.workspace_id == auth.workspace_id,
    )
    result = await db.execute(dataset_query)
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Check if already in pantry
    existing = await db.execute(
        select(KytchenDataset).where(
            KytchenDataset.kytchen_id == kytchen.id,
            KytchenDataset.dataset_id == dataset.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Dataset already in pantry")

    # Add to pantry
    pantry_item = KytchenDataset(
        kytchen_id=kytchen.id,
        dataset_id=dataset.id,
        indexed=False,
    )
    db.add(pantry_item)
    await db.commit()

    return {
        "added": True,
        "kytchen_id": _format_kitchen_id(kytchen.id),
        "dataset_id": str(dataset.id),
    }


@router.delete("/{kytchen_id}/pantry/{dataset_id}")
async def remove_from_pantry(
    kytchen_id: str,
    dataset_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Remove a dataset from the Kytchen's Pantry (86 an ingredient)."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db, require_owner=True)

    # Find pantry item
    result = await db.execute(
        select(KytchenDataset).where(
            KytchenDataset.kytchen_id == kytchen.id,
            KytchenDataset.dataset_id == dataset_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Dataset not in pantry")

    await db.delete(item)
    await db.commit()

    return {"deleted": True}


# -----------------------------------------------------------------------------
# Tickets API - Fire queries into a Kytchen
# -----------------------------------------------------------------------------


@router.post("/{kytchen_id}/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(
    kytchen_id: str,
    body: TicketCreate,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Fire a query (ticket) into a Kytchen.

    Uses the Kytchen's Pantry datasets and returns a Receipt with Sauce.
    This is the synchronous endpoint - for streaming, use /tickets/stream.
    """
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db, allow_public=True)
    kytchen_id_str = _format_kitchen_id(kytchen.id)

    # Get datasets from pantry
    dataset_ids = body.dataset_ids
    pantry_datasets = [item.dataset for item in kytchen.pantry_items if item.dataset]

    if dataset_ids:
        # Filter to specific datasets
        dataset_id_set = set(dataset_ids)
        selected = [d for d in pantry_datasets if str(d.id) in dataset_id_set]
        if len(selected) != len(dataset_id_set):
            raise HTTPException(status_code=404, detail="One or more datasets not in pantry")
    else:
        selected = pantry_datasets

    if not selected:
        raise HTTPException(status_code=400, detail="No datasets in pantry")

    # Check all datasets are ready
    for d in selected:
        if d.status != "ready":
            raise HTTPException(status_code=409, detail=f"Dataset '{d.name}' is not ready")

    # Build context from datasets
    from ..processing import get_converted_text
    from ..storage import get_storage

    storage = get_storage()
    parts: list[str] = []
    for d in selected:
        text = await get_converted_text(auth.workspace_id, str(d.id), storage)
        if text is None:
            raw = await storage.read_dataset(auth.workspace_id, str(d.id))
            text = raw.decode("utf-8", errors="replace")
        parts.append(f"=== DATASET {d.id} ({d.name}) ===\n{text or ''}")
    context_text = "\n\n".join(parts)

    # Setup provider and budget first (need budget for run record)
    from ...core import Kytchen
    from ...providers.registry import get_provider
    from ...types import Budget as KytchenBudget

    provider_name = body.provider or os.getenv("KYTCHEN_PROVIDER", "anthropic")
    model_name = body.model or os.getenv("KYTCHEN_MODEL", "claude-sonnet-4-20250514")
    provider_api_key = body.provider_api_key or ""

    provider_kwargs: dict[str, object] = {}
    if provider_api_key:
        provider_kwargs["api_key"] = provider_api_key
    provider = get_provider(provider_name, **provider_kwargs)

    # Budget from Kytchen defaults + request overrides
    budget_defaults = kytchen.budget_defaults or {}
    budget_payload = body.budget or {}
    budget = KytchenBudget(
        max_tokens=budget_payload.get("max_tokens", budget_defaults.get("max_tokens")),
        max_cost_usd=budget_payload.get("max_cost_usd", budget_defaults.get("max_cost_usd")),
        max_iterations=budget_payload.get("max_iterations", budget_defaults.get("max_iterations")),
        max_wall_time_seconds=budget_payload.get("timeout_seconds", budget_defaults.get("timeout_seconds")),
    )

    # Create run record with kytchen_id, dataset_ids, and budget
    from ..state import PostgresStore, MemoryStore

    store_instance = PostgresStore(db, storage) if not is_dev_mode() else MemoryStore()
    run = await store_instance.create_run(
        auth.workspace_id,
        query=body.query,
        kytchen_id=str(kytchen.id),
        dataset_ids=[str(d.id) for d in selected],
        budget={
            "max_tokens": budget.max_tokens,
            "max_cost_usd": budget.max_cost_usd,
            "max_iterations": budget.max_iterations,
            "timeout_seconds": budget.max_wall_time_seconds,
        },
    )

    # Execute query
    kytchen_engine = Kytchen(
        provider=provider,
        root_model=model_name,
        sub_model=model_name,
        budget=budget,
        log_trajectory=True,
    )
    resp = await kytchen_engine.complete(body.query, context_text)

    # Calculate metrics
    baseline_tokens = (len(context_text) // 4) * max(1, int(resp.total_iterations))
    metrics = TicketMetrics(
        baseline_tokens=int(baseline_tokens),
        tokens_served=int(resp.total_tokens),
        iterations=int(resp.total_iterations),
        cost_usd=float(resp.total_cost_usd),
    )

    # Update run record with answer, metrics, and status
    if not is_dev_mode():
        await store_instance.update_run(
            auth.workspace_id,
            run.id,
            answer=str(resp.answer or ""),
            success=bool(resp.success),
            error=str(resp.error) if resp.error else None,
            status="completed" if resp.success else "failed",
            metrics={
                "baseline_tokens": metrics.baseline_tokens,
                "tokens_served": metrics.tokens_served,
                "iterations": metrics.iterations,
                "cost_usd": metrics.cost_usd,
            },
        )

    return TicketResponse(
        id=run.id,
        kytchen_id=kytchen_id_str,
        query=body.query,
        status="completed" if resp.success else "failed",
        answer=resp.answer,
        evidence=resp.evidence,
        error=resp.error,
        metrics=metrics,
        created_at=run.created_at,
        completed_at=datetime.now(timezone.utc),
    )


@router.post("/{kytchen_id}/tickets/stream")
async def create_ticket_stream(
    kytchen_id: str,
    body: TicketCreate,
    request: Request,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Fire a query with SSE streaming.

    Returns Server-Sent Events with real-time progress:
    - started: Query begun
    - step: Each reasoning step
    - completed: Final answer + evidence
    - error: If something goes wrong
    """
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db, allow_public=True)
    kytchen_id_str = _format_kitchen_id(kytchen.id)

    # Get datasets from pantry
    dataset_ids = body.dataset_ids
    pantry_datasets = [item.dataset for item in kytchen.pantry_items if item.dataset]

    if dataset_ids:
        dataset_id_set = set(dataset_ids)
        selected = [d for d in pantry_datasets if str(d.id) in dataset_id_set]
        if len(selected) != len(dataset_id_set):
            raise HTTPException(status_code=404, detail="One or more datasets not in pantry")
    else:
        selected = pantry_datasets

    if not selected:
        raise HTTPException(status_code=400, detail="No datasets in pantry")

    for d in selected:
        if d.status != "ready":
            raise HTTPException(status_code=409, detail=f"Dataset '{d.name}' is not ready")

    # Build context
    from ..processing import get_converted_text
    from ..storage import get_storage

    storage = get_storage()
    parts: list[str] = []
    for d in selected:
        text = await get_converted_text(auth.workspace_id, str(d.id), storage)
        if text is None:
            raw = await storage.read_dataset(auth.workspace_id, str(d.id))
            text = raw.decode("utf-8", errors="replace")
        parts.append(f"=== DATASET {d.id} ({d.name}) ===\n{text or ''}")
    context_text = "\n\n".join(parts)

    # Setup provider and budget first
    from ...core import Kytchen
    from ...providers.registry import get_provider
    from ...types import Budget as KytchenBudget

    provider_name = body.provider or os.getenv("KYTCHEN_PROVIDER", "anthropic")
    model_name = body.model or os.getenv("KYTCHEN_MODEL", "claude-sonnet-4-20250514")
    provider_api_key = body.provider_api_key or ""

    provider_kwargs: dict[str, object] = {}
    if provider_api_key:
        provider_kwargs["api_key"] = provider_api_key
    provider = get_provider(provider_name, **provider_kwargs)

    budget_defaults = kytchen.budget_defaults or {}
    budget_payload = body.budget or {}
    budget = KytchenBudget(
        max_tokens=budget_payload.get("max_tokens", budget_defaults.get("max_tokens")),
        max_cost_usd=budget_payload.get("max_cost_usd", budget_defaults.get("max_cost_usd")),
        max_iterations=budget_payload.get("max_iterations", budget_defaults.get("max_iterations")),
        max_wall_time_seconds=budget_payload.get("timeout_seconds", budget_defaults.get("timeout_seconds")),
    )

    # Create run with kytchen_id, dataset_ids, and budget
    from ..state import PostgresStore, MemoryStore

    store_instance = PostgresStore(db, storage) if not is_dev_mode() else MemoryStore()
    run = await store_instance.create_run(
        auth.workspace_id,
        query=body.query,
        kytchen_id=str(kytchen.id),
        dataset_ids=[str(d.id) for d in selected],
        budget={
            "max_tokens": budget.max_tokens,
            "max_cost_usd": budget.max_cost_usd,
            "max_iterations": budget.max_iterations,
            "timeout_seconds": budget.max_wall_time_seconds,
        },
    )
    if not is_dev_mode():
        await db.commit()

    q: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()

    async def on_step(step: Any) -> None:
        data: dict[str, Any] = {
            "step_number": getattr(step, "step_number", None),
            "depth": getattr(step, "depth", None),
            "action_type": getattr(getattr(step, "action", None), "action_type", None).value
            if getattr(getattr(step, "action", None), "action_type", None) is not None
            else None,
            "action": getattr(getattr(step, "action", None), "content", "")[:500]
            if getattr(step, "action", None) is not None
            else "",
            "prompt_tokens": getattr(step, "prompt_tokens", None),
            "result_tokens": getattr(step, "result_tokens", None),
            "cumulative_tokens": getattr(step, "cumulative_tokens", None),
            "cumulative_cost": getattr(step, "cumulative_cost", None),
        }
        result = getattr(step, "result", None)
        if isinstance(result, str):
            data["result_preview"] = result[:500]
        else:
            stdout = getattr(result, "stdout", None)
            if isinstance(stdout, str) and stdout.strip():
                data["result_preview"] = stdout[:500]
        await q.put({"type": "step", "data": data, "timestamp": time.time()})

    async def runner() -> None:
        try:
            await q.put({
                "type": "started",
                "data": {"id": run.id, "kytchen_id": kytchen_id_str},
                "timestamp": time.time(),
            })

            kytchen_engine = Kytchen(
                provider=provider,
                root_model=model_name,
                sub_model=model_name,
                budget=budget,
                log_trajectory=True,
            )
            resp = await kytchen_engine.complete(body.query, context_text, on_step=on_step)

            baseline_tokens = (len(context_text) // 4) * max(1, int(resp.total_iterations))
            metrics = {
                "baseline_tokens": int(baseline_tokens),
                "tokens_served": int(resp.total_tokens),
                "iterations": int(resp.total_iterations),
                "cost_usd": float(resp.total_cost_usd),
            }

            if not is_dev_mode():
                await store_instance.update_run(
                    auth.workspace_id,
                    run.id,
                    answer=str(resp.answer or ""),
                    success=bool(resp.success),
                    error=str(resp.error) if resp.error else None,
                    status="completed" if resp.success else "failed",
                    metrics=metrics,
                )

            await q.put({
                "type": "completed" if resp.success else "error",
                "data": {
                    "id": run.id,
                    "kytchen_id": kytchen_id_str,
                    "answer": resp.answer,
                    "evidence": resp.evidence,
                    "metrics": metrics,
                    "error": resp.error,
                },
                "timestamp": time.time(),
            })
        except Exception as e:
            await q.put({
                "type": "error",
                "data": {"id": run.id, "kytchen_id": kytchen_id_str, "error": str(e)},
                "timestamp": time.time(),
            })
        finally:
            await q.put(None)

    task = asyncio.create_task(runner())

    async def event_stream() -> Any:
        try:
            while True:
                if await request.is_disconnected():
                    task.cancel()
                    break
                item = await q.get()
                if item is None:
                    break
                yield ("data: " + json.dumps(item) + "\n\n")
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{kytchen_id}/tickets", response_model=TicketListResponse)
async def list_tickets(
    kytchen_id: str,
    limit: int = 50,
    offset: int = 0,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> TicketListResponse:
    """List tickets (runs) for a Kytchen."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    kytchen_id_str = _format_kitchen_id(kytchen.id)

    # Query runs for this kytchen
    from ..models import Run

    count_query = select(func.count(Run.id)).where(
        Run.workspace_id == auth.workspace_id,
        Run.kytchen_id == kytchen.id,
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = (
        select(Run)
        .where(
            Run.workspace_id == auth.workspace_id,
            Run.kytchen_id == kytchen.id,
        )
        .order_by(Run.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    runs = result.scalars().all()

    return TicketListResponse(
        tickets=[
            TicketResponse(
                id=str(r.id),
                kytchen_id=kytchen_id_str,
                query=r.query or "",
                status=r.status or "pending",
                answer=r.answer,
                evidence=None,
                error=r.error,
                metrics=TicketMetrics(**r.metrics) if r.metrics else None,
                created_at=r.created_at,
                completed_at=r.completed_at,
            )
            for r in runs
        ],
        total=total,
        has_more=offset + len(runs) < total,
    )


@router.get("/{kytchen_id}/tickets/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    kytchen_id: str,
    ticket_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Get a specific ticket (run) by ID."""
    kytchen = await _resolve_kytchen(kytchen_id, auth.workspace_id, db)
    kytchen_id_str = _format_kitchen_id(kytchen.id)

    # Validate ticket_id as UUID
    import uuid as uuid_module
    try:
        uuid_module.UUID(ticket_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Ticket not found")

    from ..models import Run

    query = select(Run).where(
        Run.workspace_id == auth.workspace_id,
        Run.kytchen_id == kytchen.id,
        Run.id == ticket_id,
    )
    result = await db.execute(query)
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail="Ticket not found")

    return TicketResponse(
        id=str(run.id),
        kytchen_id=kytchen_id_str,
        query=run.query or "",
        status=run.status or "pending",
        answer=run.answer,
        evidence=None,
        error=run.error,
        metrics=TicketMetrics(**run.metrics) if run.metrics else None,
        created_at=run.created_at,
        completed_at=run.completed_at,
    )


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


async def _resolve_kitchen(
    kitchen_id: str,
    workspace_id: UUID,
    db: AsyncSession,
    require_owner: bool = False,
    allow_public: bool = False,
) -> Kytchen:
    """Resolve a Kytchen by ID or slug.

    Args:
        kitchen_id: Kytchen ID (kyt_...) or slug
        workspace_id: Current workspace ID
        db: Database session
        require_owner: If True, must belong to current workspace
        allow_public: If True, allow access to public kytchens

    Returns:
        Kytchen model

    Raises:
        HTTPException: If not found or access denied
    """
    # Try to parse as UUID (strip kyt_ prefix)
    query = (
        select(Kytchen)
        .options(selectinload(Kytchen.pantry_items).selectinload(KytchenDataset.dataset))
    )

    if kitchen_id.startswith("kyt_"):
        # Parse as Kytchen ID
        uuid_str = kitchen_id[4:]
        try:
            # Pad back to full UUID if truncated
            if len(uuid_str) == 12:
                # Query by partial match (first 12 chars of UUID hex)
                query = query.where(
                    func.replace(func.cast(Kytchen.id, String), "-", "").startswith(uuid_str)
                )
            else:
                query = query.where(Kytchen.id == uuid_str)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid kytchen ID format")
    else:
        # Treat as slug
        query = query.where(
            Kytchen.workspace_id == workspace_id,
            Kytchen.slug == kitchen_id,
        )

    result = await db.execute(query)
    kytchen = result.scalar_one_or_none()

    if not kytchen:
        raise HTTPException(status_code=404, detail="Kytchen not found")

    # Access control (compare as strings to handle UUID vs string mismatch)
    if str(kytchen.workspace_id) != str(workspace_id):
        if require_owner:
            raise HTTPException(status_code=403, detail="Access denied")
        if not allow_public or kytchen.visibility == KytchenVisibility.private:
            raise HTTPException(status_code=403, detail="Access denied")

    return kytchen


async def _resolve_kytchen(
    kytchen_id: str,
    workspace_id: UUID,
    db: AsyncSession,
    require_owner: bool = False,
    allow_public: bool = False,
) -> Kytchen:
    return await _resolve_kitchen(
        kytchen_id,
        workspace_id,
        db,
        require_owner=require_owner,
        allow_public=allow_public,
    )


def _infer_format(mime_type: str | None) -> str:
    """Infer dataset format from MIME type."""
    if not mime_type:
        return "text"
    mime_map = {
        "application/json": "json",
        "text/csv": "csv",
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
        "text/markdown": "markdown",
        "text/x-python": "code",
        "application/javascript": "code",
        "text/typescript": "code",
    }
    return mime_map.get(mime_type, "text")


# Import String for cast
from sqlalchemy import String

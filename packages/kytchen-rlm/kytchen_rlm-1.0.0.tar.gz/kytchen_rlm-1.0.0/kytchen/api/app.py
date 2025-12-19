"""FastAPI app for Kytchen Cloud v1.0.

Production backend using:
- PostgreSQL for metadata (datasets, runs, evidence, usage)
- Supabase Storage (or filesystem fallback) for dataset content
- Application-level access control (workspace isolation)
- In-memory rate limiting (can be upgraded to Redis/Valkey)

Development mode:
- Set KYTCHEN_DEV_MODE=1 to use in-memory backends (no database required)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from typing import Any

# Sentry error tracking (optional, enabled via SENTRY_DSN env var)
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    if sentry_dsn := os.getenv("SENTRY_DSN"):
        sentry_sdk.init(
            dsn=sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
            environment=os.getenv("KYTCHEN_ENV", "development"),
        )
except ImportError:
    pass  # sentry-sdk not installed, skip

try:
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
except Exception:  # pragma: no cover
    select = None  # type: ignore[assignment]
    AsyncSession = Any  # type: ignore[assignment]

from ..sandbox import SandboxConfig, get_sandbox, should_use_e2b, LocalSandbox
from ..types import ContentFormat, ContextMetadata
from .auth import WorkspaceAuth, dev_resolve_workspace, require_bearer_api_key, resolve_workspace
from .db import AsyncSessionLocal, close_db, get_db, init_db
from .limits import get_plan_limits
from .state import (
    EvidenceRecord,
    MemoryRateLimiter,
    MemoryStore,
    MemoryUsageTracker,
    PostgresStore,
    PostgresUsageTracker,
    ToolSession,
)
from .storage import get_storage

try:
    from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
    from fastapi.responses import JSONResponse, StreamingResponse
except Exception as e:  # pragma: no cover
    raise RuntimeError("Kytchen Cloud API requires FastAPI. Install `pip install 'kytchen[api]'`.") from e

from .audit import AuditLogger, EventType, MemoryAuditLogger
from .processing import process_dataset


def _detect_format(text: str) -> ContentFormat:
    t = text.lstrip()
    if t.startswith("{") or t.startswith("["):
        try:
            json.loads(text)
            return ContentFormat.JSON
        except Exception:
            return ContentFormat.TEXT
    return ContentFormat.TEXT


def _analyze_text_context(text: str, fmt: ContentFormat) -> ContextMetadata:
    return ContextMetadata(
        format=fmt,
        size_bytes=len(text.encode("utf-8", errors="ignore")),
        size_chars=len(text),
        size_lines=text.count("\n") + 1,
        size_tokens_estimate=len(text) // 4,
        structure_hint=None,
        sample_preview=text[:500],
    )


def is_dev_mode() -> bool:
    """Check if running in development mode (no database required)."""
    if select is None:
        return True
    return os.getenv("KYTCHEN_DEV_MODE", "0").strip() in ("1", "true", "yes")


def is_self_host() -> bool:
    return os.getenv("KYTCHEN_SELF_HOST", "0").strip() in ("1", "true", "yes")


async def bootstrap_self_host() -> None:
    """Ensure a default workspace + API key exist for self-host deployments.

    This is intentionally minimal: it creates only the records required for
    API-key auth to succeed against an empty database.
    """
    if not is_self_host():
        return

    bootstrap_api_key = os.getenv("KYTCHEN_BOOTSTRAP_API_KEY", "").strip()
    if not bootstrap_api_key:
        return
    if not bootstrap_api_key.startswith("kyt_sk_"):
        raise RuntimeError("KYTCHEN_BOOTSTRAP_API_KEY must start with kyt_sk_")

    slug = os.getenv("KYTCHEN_BOOTSTRAP_WORKSPACE_SLUG", "default").strip() or "default"
    name = os.getenv("KYTCHEN_BOOTSTRAP_WORKSPACE_NAME", "Default Workspace").strip() or "Default Workspace"
    plan = os.getenv("KYTCHEN_BOOTSTRAP_PLAN", "free").strip().lower() or "free"
    key_name = os.getenv("KYTCHEN_BOOTSTRAP_API_KEY_NAME", "Self-host bootstrap key").strip() or "Self-host bootstrap key"

    from .auth import hash_api_key
    from .models import APIKey, Workspace, WorkspacePlan

    key_hash = hash_api_key(bootstrap_api_key)
    key_prefix = bootstrap_api_key[:12]

    try:
        plan_enum = WorkspacePlan(plan)
    except Exception:
        plan_enum = WorkspacePlan.free

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Workspace).where(Workspace.slug == slug))
        workspace = result.scalar_one_or_none()
        if workspace is None:
            workspace = Workspace(slug=slug, name=name, plan=plan_enum)
            session.add(workspace)
            await session.flush()

        result = await session.execute(select(APIKey).where(APIKey.key_hash == key_hash))
        existing_key = result.scalar_one_or_none()
        if existing_key is None:
            session.add(
                APIKey(
                    workspace_id=workspace.id,
                    key_hash=key_hash,
                    key_prefix=key_prefix,
                    name=key_name,
                )
            )

        await session.commit()


async def get_auth(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceAuth:
    """FastAPI dependency for authentication.

    In production mode: looks up API key in database
    In dev mode: generates deterministic workspace ID

    Args:
        authorization: Authorization header
        db: Database session (ignored in dev mode)

    Returns:
        WorkspaceAuth with workspace_id and plan

    Raises:
        HTTPException: If auth fails
    """
    try:
        api_key = require_bearer_api_key(authorization)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Development mode: no database lookup
    if is_dev_mode():
        return dev_resolve_workspace(api_key)

    # Production mode: database lookup
    try:
        return await resolve_workspace(api_key, db)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


def create_app() -> FastAPI:
    app = FastAPI(
        title="Kytchen Cloud API",
        version="1.0.0",
        description=(
            "Kytchen Cloud API - BYOLLM context processing with sandboxed execution.\n\n"
            "## Features\n"
            "- **Datasets (Pantry)**: Upload and manage datasets for context processing\n"
            "- **Query**: Run natural language queries against datasets using your LLM\n"
            "- **Tools (Prep)**: Execute sandboxed Python code, search, and peek context\n"
            "- **Evidence (Sauce)**: Track and export evidence from analysis runs\n\n"
            "## Authentication\n"
            "All endpoints (except /healthz) require Bearer token authentication:\n"
            "`Authorization: Bearer kyt_sk_...`\n\n"
            "Get your API key at https://kytchen.dev"
        ),
        openapi_tags=[
            {"name": "health", "description": "Health check endpoints"},
            {"name": "datasets", "description": "Dataset (pantry) management"},
            {"name": "query", "description": "Query execution"},
            {"name": "tools", "description": "Tool execution endpoints"},
            {"name": "auth", "description": "Authentication endpoints"},
            {"name": "keys", "description": "API key management"},
            {"name": "billing", "description": "Billing and subscription management"},
        ],
    )

    # Development mode: in-memory backends
    if is_dev_mode():
        print("[Kytchen] Running in DEV MODE (no database required)")
        store = MemoryStore()
        usage = MemoryUsageTracker()
        limiter = MemoryRateLimiter()
        use_db = False
    else:
        if select is None:
            raise RuntimeError("Kytchen Cloud API database mode requires SQLAlchemy. Install `pip install 'kytchen[api]'`.")
        print("[Kytchen] Running in PRODUCTION MODE (PostgreSQL + Storage)")
        store = None  # Will be created per-request with DB session
        usage = None  # Will be created per-request with DB session
        limiter = MemoryRateLimiter()  # Still in-memory (upgrade to Redis later)
        use_db = True

    @app.on_event("startup")
    async def startup() -> None:
        """Initialize database on startup."""
        if is_dev_mode():
            print("[Kytchen] Initializing database (dev mode - SQLite)...")
            await init_db()
            print("[Kytchen] Database ready (SQLite in-memory)")
        else:
            print("[Kytchen] Initializing database...")
            await init_db()
            await bootstrap_self_host()
            print("[Kytchen] Database ready")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        """Close database connections on shutdown."""
        print("[Kytchen] Closing database...")
        await close_db()
        print("[Kytchen] Database closed")

    @app.middleware("http")
    async def limits_middleware(request, call_next):  # type: ignore[no-untyped-def]
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            api_key = auth_header.split(None, 1)[1].strip()
            if api_key.startswith("kyt_sk_"):
                # Use the workspace plan to determine rate limits.
                # Dev mode: plan comes from env; Prod mode: plan comes from DB lookup.
                if is_dev_mode():
                    limits = get_plan_limits(os.getenv("KYTCHEN_DEV_PLAN", "free"))
                else:
                    from .auth import hash_api_key
                    from .models import APIKey, Workspace

                    plan = "free"
                    try:
                        async with AsyncSessionLocal() as session:
                            key_hash = hash_api_key(api_key)
                            result = await session.execute(
                                select(Workspace.plan)
                                .join(APIKey, APIKey.workspace_id == Workspace.id)
                                .where(
                                    APIKey.key_hash == key_hash,
                                    APIKey.revoked_at.is_(None),
                                )
                            )
                            row = result.first()
                            if row and row[0] is not None:
                                plan = str(getattr(row[0], "value", row[0]))
                    except Exception:
                        plan = "free"

                    limits = get_plan_limits(plan)
                try:
                    await limiter.check(api_key, limits.rate_limit_per_min)
                except RuntimeError:
                    return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
        return await call_next(request)

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    # ------------------------------------------------------------------
    # Datasets (ingredients) - memory implementation
    # ------------------------------------------------------------------

    @app.get("/v1/datasets")
    async def list_datasets(
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, Any]:
        # Get store instance (dev: global, prod: per-request)
        if use_db:
            store_instance = PostgresStore(db, get_storage())
        else:
            store_instance = store

        datasets = await store_instance.list_datasets(auth.workspace_id)
        return {
            "datasets": [
                {
                    "id": d.id,
                    "name": d.name,
                    "size_bytes": d.size_bytes,
                    "format": None,
                    "content_hash": d.content_hash,
                    "created_at": d.created_at,
                    "status": d.status,
                    "processing_error": d.processing_error,
                }
                for d in datasets
            ]
        }

    @app.post("/v1/datasets")
    async def upload_dataset(
        request: Request,
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        name: str | None = Form(default=None),
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, Any]:
        if name is None:
            name = request.query_params.get("name")
        if not name:
            raise HTTPException(status_code=400, detail="Missing name")

        # Get store and usage instances
        storage = get_storage()
        if use_db:
            store_instance = PostgresStore(db, storage)
            usage_instance = PostgresUsageTracker(db)
            audit_logger: AuditLogger | MemoryAuditLogger | None = AuditLogger(db)
        else:
            store_instance = store
            usage_instance = usage
            audit_logger = None  # Skip audit in dev mode

        limits = auth.limits
        content = await file.read()
        used = await usage_instance.storage_used(auth.workspace_id)
        if used + len(content) > limits.pantry_storage_bytes:
            raise HTTPException(status_code=402, detail="Storage limit reached")

        content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
        rec = await store_instance.create_dataset(
            auth.workspace_id,
            name=name,
            content=content,
            content_hash=content_hash,
            mime_type=file.content_type,
            status="uploaded",  # Start with 'uploaded', processing will update to 'ready'
        )
        await usage_instance.add_storage(auth.workspace_id, rec.size_bytes)

        # Emit audit event for upload
        if audit_logger is not None:
            await audit_logger.log(
                workspace_id=auth.workspace_id,
                event_type=EventType.DATASET_UPLOADED,
                actor_type="api_key",
                actor_id=auth.api_key_id,
                resource_type="dataset",
                resource_id=rec.id,
                description=f"Dataset '{name}' uploaded",
                metadata={
                    "name": name,
                    "size_bytes": rec.size_bytes,
                    "mime_type": file.content_type,
                },
            )

        # Schedule background processing (for binary files like PDF, DOCX, XLSX)
        # For text files, processing will just store the content as-is
        background_tasks.add_task(
            _process_dataset_task,
            dataset_id=rec.id,
            workspace_id=auth.workspace_id,
            content=content,
            mime_type=file.content_type,
            use_db=use_db,
        )

        return {
            "id": rec.id,
            "name": rec.name,
            "size_bytes": rec.size_bytes,
            "content_hash": rec.content_hash,
            "created_at": rec.created_at,
            "status": rec.status,
        }

    async def _process_dataset_task(
        dataset_id: str,
        workspace_id: str,
        content: bytes,
        mime_type: str | None,
        use_db: bool,
    ) -> None:
        """Background task to process uploaded dataset."""
        if not use_db:
            # In dev mode, skip processing (already stored as-is)
            return

        # Create fresh database session for background task
        from .db import engine
        from sqlalchemy.ext.asyncio import AsyncSession

        async with AsyncSession(engine) as session:
            storage = get_storage()
            audit_logger = AuditLogger(session)
            await process_dataset(
                dataset_id=dataset_id,
                workspace_id=workspace_id,
                content=content,
                mime_type=mime_type,
                db=session,
                storage=storage,
                audit_logger=audit_logger,
            )

    @app.get("/v1/datasets/{dataset_id}")
    async def get_dataset(
        dataset_id: str,
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, Any]:
        """Get a single dataset by ID."""
        if use_db:
            store_instance = PostgresStore(db, get_storage())
        else:
            store_instance = store

        rec = await store_instance.get_dataset(auth.workspace_id, dataset_id)
        if rec is None:
            raise HTTPException(status_code=404, detail="Dataset not found")

        return {
            "id": rec.id,
            "name": rec.name,
            "size_bytes": rec.size_bytes,
            "content_hash": rec.content_hash,
            "mime_type": rec.mime_type,
            "created_at": rec.created_at,
            "status": rec.status,
            "processing_error": rec.processing_error,
        }

    @app.delete("/v1/datasets/{dataset_id}")
    async def delete_dataset(
        dataset_id: str,
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, Any]:
        # Get store and usage instances
        if use_db:
            store_instance = PostgresStore(db, get_storage())
            usage_instance = PostgresUsageTracker(db)
            audit_logger: AuditLogger | MemoryAuditLogger | None = AuditLogger(db)
        else:
            store_instance = store
            usage_instance = usage
            audit_logger = None

        rec = await store_instance.delete_dataset(auth.workspace_id, dataset_id)
        if rec is None:
            raise HTTPException(status_code=404, detail="Dataset not found")
        await usage_instance.sub_storage(auth.workspace_id, rec.size_bytes)

        # Emit audit event for deletion
        if audit_logger is not None:
            await audit_logger.log(
                workspace_id=auth.workspace_id,
                event_type=EventType.DATASET_DELETED,
                actor_type="api_key",
                actor_id=auth.api_key_id,
                resource_type="dataset",
                resource_id=dataset_id,
                description=f"Dataset '{rec.name}' deleted",
                metadata={
                    "name": rec.name,
                    "size_bytes": rec.size_bytes,
                },
            )

        return {"deleted": True}

    # ------------------------------------------------------------------
    # Runs (tickets)
    # ------------------------------------------------------------------

    @app.post("/v1/query")
    async def start_query(
        payload: dict[str, Any],
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, Any]:
        def _coerce_str(v: object | None) -> str:
            return v.strip() if isinstance(v, str) else str(v or "").strip()

        query_text = _coerce_str(payload.get("query") or payload.get("prompt"))
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing query")

        dataset_ids = payload.get("dataset_ids")
        if dataset_ids is None:
            dataset_id = payload.get("datasetId")
            dataset_ids = [dataset_id] if dataset_id else None

        if dataset_ids is not None:
            if not isinstance(dataset_ids, list) or not all(isinstance(x, str) for x in dataset_ids):
                raise HTTPException(status_code=400, detail="dataset_ids must be a list of strings")

        budget_payload = payload.get("budget")
        if budget_payload is not None and not isinstance(budget_payload, dict):
            raise HTTPException(status_code=400, detail="budget must be an object")
        budget_payload = dict(budget_payload or {})
        if "maxCost" in budget_payload and "max_cost_usd" not in budget_payload:
            budget_payload["max_cost_usd"] = budget_payload.get("maxCost")
        if "maxIterations" in budget_payload and "max_iterations" not in budget_payload:
            budget_payload["max_iterations"] = budget_payload.get("maxIterations")
        if "maxTokens" in budget_payload and "max_tokens" not in budget_payload:
            budget_payload["max_tokens"] = budget_payload.get("maxTokens")
        if "maxWallTimeSeconds" in budget_payload and "max_wall_time_seconds" not in budget_payload:
            budget_payload["max_wall_time_seconds"] = budget_payload.get("maxWallTimeSeconds")

        provider_name = _coerce_str(payload.get("provider") or os.getenv("KYTCHEN_PROVIDER", "anthropic"))
        model_name = _coerce_str(payload.get("model") or os.getenv("KYTCHEN_MODEL", "claude-sonnet-4-20250514"))
        provider_api_key = payload.get("provider_api_key") or payload.get("providerApiKey")
        provider_api_key = _coerce_str(provider_api_key) if provider_api_key is not None else ""

        storage = get_storage()
        if use_db:
            store_instance = PostgresStore(db, storage)
        else:
            store_instance = store

        run = await store_instance.create_run(auth.workspace_id, query=query_text)

        all_datasets = await store_instance.list_datasets(auth.workspace_id)
        selected = all_datasets if dataset_ids is None else [d for d in all_datasets if d.id in set(dataset_ids)]
        if dataset_ids is not None and len(selected) != len(set(dataset_ids)):
            raise HTTPException(status_code=404, detail="One or more datasets not found")

        for d in selected:
            if d.status != "ready":
                raise HTTPException(status_code=409, detail="One or more datasets are not ready")

        from .processing import get_converted_text

        parts: list[str] = []
        for d in selected:
            text = None
            if use_db:
                text = await get_converted_text(auth.workspace_id, d.id, storage)
            if text is None:
                if hasattr(store_instance, "_dataset_bytes"):
                    raw = store_instance._dataset_bytes.get(auth.workspace_id, {}).get(d.id)  # type: ignore[attr-defined]
                    if isinstance(raw, (bytes, bytearray)):
                        text = raw.decode("utf-8", errors="replace")
                if text is None and use_db:
                    raw = await storage.read_dataset(auth.workspace_id, d.id)
                    text = raw.decode("utf-8", errors="replace")

            parts.append(f"=== DATASET {d.id} ({d.name}) ===\n{text or ''}")

        context_text = "\n\n".join(parts)

        from ..core import Kytchen
        from ..providers.registry import get_provider
        from ..types import Budget as KytchenBudget

        provider_kwargs: dict[str, object] = {}
        if provider_api_key:
            provider_kwargs["api_key"] = provider_api_key
        provider = get_provider(provider_name, **provider_kwargs)
        budget = KytchenBudget(
            max_tokens=budget_payload.get("max_tokens"),
            max_cost_usd=budget_payload.get("max_cost_usd"),
            max_iterations=budget_payload.get("max_iterations"),
            max_wall_time_seconds=budget_payload.get("max_wall_time_seconds"),
            max_depth=budget_payload.get("max_depth"),
            max_sub_queries=budget_payload.get("max_sub_queries"),
        )

        kytchen = Kytchen(provider=provider, root_model=model_name, sub_model=model_name, budget=budget, log_trajectory=True)
        resp = await kytchen.complete(query_text, context_text)

        baseline_tokens = (len(context_text) // 4) * max(1, int(resp.total_iterations))
        metrics = {
            "baseline_tokens": int(baseline_tokens),
            "tokens_served": int(resp.total_tokens),
            "iterations": int(resp.total_iterations),
            "cost_usd": float(resp.total_cost_usd),
        }

        if use_db:
            await store_instance.update_run(
                auth.workspace_id,
                run.id,
                answer=str(resp.answer or ""),
                success=bool(resp.success),
                error=str(resp.error) if resp.error else None,
                status="completed" if resp.success else "failed",
            )
            try:
                from sqlalchemy import update
                from .models import Run

                await db.execute(
                    update(Run)
                    .where(Run.workspace_id == auth.workspace_id, Run.id == run.id)
                    .values(metrics=metrics)
                )
            except Exception:
                pass

        return {
            "id": run.id,
            "answer": resp.answer,
            "evidence": resp.evidence,
            "metrics": metrics,
        }


    @app.post("/v1/query/stream")
    async def query_stream(
        request: Request,
        payload: dict[str, Any],
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> StreamingResponse:
        def _coerce_str(v: object | None) -> str:
            return v.strip() if isinstance(v, str) else str(v or "").strip()

        query_text = _coerce_str(payload.get("query") or payload.get("prompt"))
        if not query_text:
            raise HTTPException(status_code=400, detail="Missing query")

        dataset_ids = payload.get("dataset_ids")
        if dataset_ids is None:
            dataset_id = payload.get("datasetId")
            dataset_ids = [dataset_id] if dataset_id else None

        if dataset_ids is not None:
            if not isinstance(dataset_ids, list) or not all(isinstance(x, str) for x in dataset_ids):
                raise HTTPException(status_code=400, detail="dataset_ids must be a list of strings")

        budget_payload = payload.get("budget")
        if budget_payload is not None and not isinstance(budget_payload, dict):
            raise HTTPException(status_code=400, detail="budget must be an object")
        budget_payload = dict(budget_payload or {})
        if "maxCost" in budget_payload and "max_cost_usd" not in budget_payload:
            budget_payload["max_cost_usd"] = budget_payload.get("maxCost")
        if "maxIterations" in budget_payload and "max_iterations" not in budget_payload:
            budget_payload["max_iterations"] = budget_payload.get("maxIterations")
        if "maxTokens" in budget_payload and "max_tokens" not in budget_payload:
            budget_payload["max_tokens"] = budget_payload.get("maxTokens")
        if "maxWallTimeSeconds" in budget_payload and "max_wall_time_seconds" not in budget_payload:
            budget_payload["max_wall_time_seconds"] = budget_payload.get("maxWallTimeSeconds")

        provider_name = _coerce_str(payload.get("provider") or os.getenv("KYTCHEN_PROVIDER", "anthropic"))
        model_name = _coerce_str(payload.get("model") or os.getenv("KYTCHEN_MODEL", "claude-sonnet-4-20250514"))
        provider_api_key = payload.get("provider_api_key") or payload.get("providerApiKey")
        provider_api_key = _coerce_str(provider_api_key) if provider_api_key is not None else ""

        storage = get_storage()
        if use_db:
            store_instance = PostgresStore(db, storage)
        else:
            store_instance = store

        run = await store_instance.create_run(auth.workspace_id, query=query_text)
        if use_db:
            await db.commit()

        all_datasets = await store_instance.list_datasets(auth.workspace_id)
        selected = all_datasets if dataset_ids is None else [d for d in all_datasets if d.id in set(dataset_ids)]
        if dataset_ids is not None and len(selected) != len(set(dataset_ids)):
            raise HTTPException(status_code=404, detail="One or more datasets not found")
        for d in selected:
            if d.status != "ready":
                raise HTTPException(status_code=409, detail="One or more datasets are not ready")

        from .processing import get_converted_text

        parts: list[str] = []
        for d in selected:
            text = None
            if use_db:
                text = await get_converted_text(auth.workspace_id, d.id, storage)
            if text is None:
                if hasattr(store_instance, "_dataset_bytes"):
                    raw = store_instance._dataset_bytes.get(auth.workspace_id, {}).get(d.id)  # type: ignore[attr-defined]
                    if isinstance(raw, (bytes, bytearray)):
                        text = raw.decode("utf-8", errors="replace")
                if text is None and use_db:
                    raw = await storage.read_dataset(auth.workspace_id, d.id)
                    text = raw.decode("utf-8", errors="replace")
            parts.append(f"=== DATASET {d.id} ({d.name}) ===\n{text or ''}")
        context_text = "\n\n".join(parts)

        from ..core import Kytchen
        from ..providers.registry import get_provider
        from ..types import Budget as KytchenBudget

        provider_kwargs: dict[str, object] = {}
        if provider_api_key:
            provider_kwargs["api_key"] = provider_api_key
        provider = get_provider(provider_name, **provider_kwargs)
        budget = KytchenBudget(
            max_tokens=budget_payload.get("max_tokens"),
            max_cost_usd=budget_payload.get("max_cost_usd"),
            max_iterations=budget_payload.get("max_iterations"),
            max_wall_time_seconds=budget_payload.get("max_wall_time_seconds"),
            max_depth=budget_payload.get("max_depth"),
            max_sub_queries=budget_payload.get("max_sub_queries"),
        )

        q: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()

        async def on_step(step) -> None:  # type: ignore[no-untyped-def]
            data: dict[str, Any] = {
                "step_number": getattr(step, "step_number", None),
                "depth": getattr(step, "depth", None),
                "action_type": getattr(getattr(step, "action", None), "action_type", None).value if getattr(getattr(step, "action", None), "action_type", None) is not None else None,
                "action": getattr(getattr(step, "action", None), "content", "")[:500] if getattr(step, "action", None) is not None else "",
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

            await q.put({"type": "step", "data": data, "timestamp": getattr(getattr(step, "timestamp", None), "timestamp", lambda: time.time())()})

        async def runner() -> None:
            try:
                await q.put({"type": "started", "data": {"id": run.id}, "timestamp": time.time()})
                kytchen = Kytchen(provider=provider, root_model=model_name, sub_model=model_name, budget=budget, log_trajectory=True)
                resp = await kytchen.complete(query_text, context_text, on_step=on_step)

                baseline_tokens = (len(context_text) // 4) * max(1, int(resp.total_iterations))
                metrics = {
                    "baseline_tokens": int(baseline_tokens),
                    "tokens_served": int(resp.total_tokens),
                    "iterations": int(resp.total_iterations),
                    "cost_usd": float(resp.total_cost_usd),
                }

                if use_db:
                    await store_instance.update_run(
                        auth.workspace_id,
                        run.id,
                        answer=str(resp.answer or ""),
                        success=bool(resp.success),
                        error=str(resp.error) if resp.error else None,
                        status="completed" if resp.success else "failed",
                    )
                    try:
                        from sqlalchemy import update
                        from .models import Run

                        await db.execute(
                            update(Run)
                            .where(Run.workspace_id == auth.workspace_id, Run.id == run.id)
                            .values(metrics=metrics)
                        )
                    except Exception:
                        pass

                await q.put(
                    {
                        "type": "completed" if resp.success else "error",
                        "data": {
                            "id": run.id,
                            "answer": resp.answer,
                            "evidence": resp.evidence,
                            "metrics": metrics,
                            "error": resp.error,
                        },
                        "timestamp": time.time(),
                    }
                )
            except Exception as e:
                await q.put({"type": "error", "data": {"id": run.id, "error": str(e)}, "timestamp": time.time()})
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

    @app.post("/v1/runs/{run_id}/finalize")
    async def finalize_run(
        run_id: str,
        payload: dict[str, Any],
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> dict[str, Any]:
        # Get store instance
        if use_db:
            store_instance = PostgresStore(db, get_storage())
        else:
            store_instance = store

        # In dev mode, mutate in-place; in prod mode, use update method
        if use_db:
            answer = payload.get("answer")
            success = payload.get("success")
            error = payload.get("error")
            status = "completed" if success else "failed"

            run = await store_instance.update_run(
                auth.workspace_id,
                run_id,
                answer=str(answer) if answer is not None else None,
                success=bool(success) if success is not None else None,
                error=str(error) if error is not None else None,
                status=status,
            )
            if run is None:
                raise HTTPException(status_code=404, detail="Run not found")
        else:
            run = await store_instance.get_run(auth.workspace_id, run_id)
            if run is None:
                raise HTTPException(status_code=404, detail="Run not found")
            answer = payload.get("answer")
            success = payload.get("success")
            error = payload.get("error")
            run.answer = str(answer) if answer is not None else None
            run.success = bool(success) if success is not None else None
            run.error = str(error) if error is not None else None
            run.status = "completed" if run.success else "failed"

        return {"id": run.id, "status": run.status}

    # ------------------------------------------------------------------
    # Tool loop (prep)
    # ------------------------------------------------------------------

    async def _get_session(auth: WorkspaceAuth, context_id: str, db: AsyncSession | None = None) -> ToolSession | None:
        if use_db and db:
            store_instance = PostgresStore(db, get_storage())
        else:
            store_instance = store
        return await store_instance.get_session(auth.workspace_id, context_id)

    async def _set_session(auth: WorkspaceAuth, context_id: str, session: ToolSession, db: AsyncSession | None = None) -> None:
        if use_db and db:
            store_instance = PostgresStore(db, get_storage())
        else:
            store_instance = store
        await store_instance.upsert_session(auth.workspace_id, context_id, session)

    @app.post("/v1/tool/{name}")
    async def tool_call(
        name: str,
        payload: dict[str, Any],
        auth: WorkspaceAuth = Depends(get_auth),
        db: AsyncSession = Depends(get_db),
    ) -> JSONResponse:
        limits = auth.limits

        # Get usage instance
        if use_db:
            usage_instance = PostgresUsageTracker(db)
        else:
            usage_instance = usage

        async def _result() -> str:
            context_id = str(payload.get("context_id", "default"))
            session = await _get_session(auth, context_id, db if use_db else None)

            if name == "load_context":
                context = str(payload.get("context", ""))
                format_str = str(payload.get("format", "auto"))
                fmt = _detect_format(context) if format_str == "auto" else ContentFormat(format_str)
                meta = _analyze_text_context(context, fmt)

                # Create sandbox using the abstraction layer
                # In dev mode or when E2B is not configured, uses local sandbox
                sandbox_config = SandboxConfig(
                    timeout_seconds=float(limits.tool_timeout_seconds),
                    max_output_chars=10_000,
                )

                # Get appropriate sandbox (E2B in prod, local in dev)
                sandbox = await get_sandbox(
                    workspace_id=auth.workspace_id,
                    config=sandbox_config,
                    context=context,
                    force_local=is_dev_mode(),  # Force local in dev mode
                )

                # For backwards compatibility, also create repl for local sandbox
                repl = None
                if isinstance(sandbox, LocalSandbox):
                    repl = sandbox._repl

                s = ToolSession(
                    repl=repl,
                    sandbox=sandbox,
                    meta=meta,
                    sandbox_id=sandbox.sandbox_id,
                )
                await _set_session(auth, context_id, s, db if use_db else None)

                sandbox_type = "E2B" if should_use_e2b() and not is_dev_mode() else "local"
                return f"Loaded context '{context_id}' ({sandbox_type}): {meta.size_chars:,} chars, {meta.size_lines:,} lines, ~{meta.size_tokens_estimate:,} tokens"

            if session is None:
                return f"Error: No context loaded with ID '{context_id}'. Use load_context first."

            session.iterations += 1

            if name == "peek_context":
                start = int(payload.get("start", 0))
                end = payload.get("end")
                end_i = int(end) if end is not None else None
                unit = payload.get("unit", "chars")
                helper_name = "peek" if unit == "chars" else "lines"

                # Use local repl if available (faster), otherwise execute via sandbox
                if session.repl is not None:
                    fn = session.repl.get_variable(helper_name)
                    if callable(fn):
                        out = fn(start, end_i)
                    else:
                        out = ""
                elif session.sandbox is not None:
                    # Execute via sandbox for E2B
                    code = f"{helper_name}({start}, {end_i})"
                    res = await session.sandbox.execute(code)
                    out = res.return_value if res.return_value else res.stdout
                else:
                    return "Error: No sandbox or repl available in session"

                if out:
                    session.evidence.append(EvidenceRecord(tool_name="peek_context", params=payload, snippet=str(out)[:200], line_range=None, note=None))
                return str(out)

            if name == "search_context":
                pattern = str(payload.get("pattern", ""))
                max_results = int(payload.get("max_results", 10))
                context_lines = int(payload.get("context_lines", 2))

                # Use local repl if available (faster), otherwise execute via sandbox
                if session.repl is not None:
                    fn = session.repl.get_variable("search")
                    if not callable(fn):
                        return "Error: search() helper is not available"
                    results = fn(pattern, context_lines=context_lines, max_results=max_results)
                elif session.sandbox is not None:
                    # Execute via sandbox for E2B
                    code = f"search({repr(pattern)}, context_lines={context_lines}, max_results={max_results})"
                    res = await session.sandbox.execute(code)
                    if res.error:
                        return f"Error: {res.error}"
                    # Parse results from sandbox output
                    try:
                        results = json.loads(res.return_value) if res.return_value else []
                    except Exception:
                        results = []
                else:
                    return "Error: No sandbox or repl available in session"

                if not results:
                    return "No matches found."
                out_lines: list[str] = []
                for r in results:
                    try:
                        line_num = r.get("line_num") or r.get("line_number", 0)
                        out_lines.append(f"Line {line_num}:\n{r.get('context', '')}")
                        session.evidence.append(
                            EvidenceRecord(
                                tool_name="search_context",
                                params=payload,
                                snippet=str(r.get("match", ""))[:200],
                                line_range=(max(0, int(line_num) - context_lines), int(line_num) + context_lines),
                                note=None,
                            )
                        )
                    except Exception:
                        out_lines.append(str(r))
                return "\n---\n".join(out_lines)

            if name == "exec_python":
                code = str(payload.get("code", ""))

                async def _exec() -> str:
                    # Use sandbox abstraction if available, fall back to repl
                    if session.sandbox is not None:
                        res = await session.sandbox.execute(code)
                    elif session.repl is not None:
                        res = await session.repl.execute_async(code)
                    else:
                        return "Error: No sandbox or repl available in session"

                    out = res.stdout
                    if res.stderr:
                        out += f"\n[STDERR]: {res.stderr}"
                    if res.error:
                        out += f"\n[ERROR]: {res.error}"
                    if res.return_value is not None:
                        out += f"\n[RETURN_VALUE]: {res.return_value}"
                    return out or "(no output)"

                out = await asyncio.wait_for(_exec(), timeout=float(limits.tool_timeout_seconds))
                session.evidence.append(EvidenceRecord(tool_name="exec_python", params={"code_preview": code[:200]}, snippet=out[:200], line_range=None, note=None))
                return out

            if name == "get_variable":
                var_name = str(payload.get("name", ""))
                # Use sandbox abstraction if available
                if session.sandbox is not None:
                    value = await session.sandbox.get_variable(var_name)
                elif session.repl is not None:
                    value = session.repl.get_variable(var_name)
                else:
                    return "Error: No sandbox or repl available in session"
                return f"Variable '{var_name}' not found" if value is None else str(value)

            if name == "think":
                question = str(payload.get("question", ""))
                session.think_history.append(question)
                return f"Reasoning step: {question}"

            if name == "get_status":
                parts = [
                    "## Session Status",
                    f"**Workspace:** `{auth.workspace_id}`",
                    f"**Session ID:** `{context_id}`",
                    f"**Iterations:** {session.iterations}",
                    f"- Sauce items: {len(session.evidence)}",
                ]
                return "\n".join(parts)

            if name == "get_evidence":
                limit = int(payload.get("limit", 20))
                offset = int(payload.get("offset", 0))
                output = payload.get("output", "markdown")
                page = session.evidence[max(0, offset) : max(0, offset) + (20 if limit <= 0 else limit)]
                if output == "json":
                    return json.dumps(
                        {
                            "context_id": context_id,
                            "total": len(session.evidence),
                            "items": [
                                {
                                    "tool_name": ev.tool_name,
                                    "line_range": ev.line_range,
                                    "note": ev.note,
                                    "snippet": ev.snippet,
                                }
                                for ev in page
                            ],
                        }
                    )
                return "\n".join(f"- [{ev.tool_name}] {ev.snippet}" for ev in page) or "(no sauce)"

            if name == "finalize":
                answer = str(payload.get("answer", ""))
                confidence = str(payload.get("confidence", "medium"))
                session.finalized_answer = answer
                parts = ["## Final Answer", answer, f"**Confidence:** {confidence}"]
                if session.evidence:
                    parts.append("### Sauce")
                    for ev in session.evidence[-10:]:
                        parts.append(f"- [{ev.tool_name}]: {ev.snippet[:80]}")
                return "\n".join(parts)

            return f"Error: Unknown tool '{name}'"

        try:
            result = await _result()
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Tool timeout")

        body = {"result": result}
        body_bytes = JSONResponse(body).body
        try:
            await usage_instance.add_egress_or_reject(auth.workspace_id, len(body_bytes), auth.limits.egress_bytes_per_month)
        except RuntimeError:
            raise HTTPException(status_code=402, detail="Egress limit reached")
        return JSONResponse(body)

    # ------------------------------------------------------------------
    # Auth Routes
    # ------------------------------------------------------------------
    from .routes.auth import router as auth_router

    app.include_router(auth_router)

    # ------------------------------------------------------------------
    # Kytchen Routes (SHA-107: Menu API)
    # ------------------------------------------------------------------
    try:
        from .routes.kytchens import router as kytchens_router

        app.include_router(kytchens_router)
    except Exception:
        # Optional: these routes require SQLAlchemy. In environments without
        # `kytchen[api]`, skip registering them.
        pass

    # ------------------------------------------------------------------
    # Git Routes
    # ------------------------------------------------------------------
    try:
        from .routes.git import router as git_router

        app.include_router(git_router)
    except Exception:
        # Optional: git routes require SQLAlchemy. Skip if not available.
        pass

    # ------------------------------------------------------------------
    # Lines Routes (SHA-117: E2B Sandbox Management)
    # ------------------------------------------------------------------
    try:
        from .routes.lines import router as lines_router

        app.include_router(lines_router)
    except Exception:
        # Optional: lines routes require E2B SDK and SQLAlchemy. Skip if not available.
        pass

    # ------------------------------------------------------------------
    # Keys Routes
    # ------------------------------------------------------------------
    try:
        from .routes.keys import router as keys_router

        app.include_router(keys_router)
    except Exception:
        # Optional: these routes require SQLAlchemy. In environments without
        # `kytchen[api]`, skip registering them.
        pass

    # ------------------------------------------------------------------
    # Billing Routes (SHA-113: Stripe Integration)
    # ------------------------------------------------------------------
    try:
        from .routes.billing import router as billing_router

        app.include_router(billing_router)
    except Exception:
        # Optional: billing routes require Stripe. Skip if not configured.
        pass

    return app


app = create_app()


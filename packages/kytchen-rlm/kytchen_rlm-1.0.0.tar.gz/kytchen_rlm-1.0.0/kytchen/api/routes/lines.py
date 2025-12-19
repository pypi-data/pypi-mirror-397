"""E2B Line (sandbox) API routes.

Lines are Kytchen's term for E2B sandboxes - isolated execution environments
that persist across requests. Each Line is bound to a Kytchen and tracked
in the SandboxSession table.

Tier limits:
- Starter (free): 0 lines (no E2B access)
- Chef ($35/mo): 1 line
- Sous Chef ($99/mo): 3 lines

"A line cook preps the mise en place. A Line preps the code."
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import WorkspaceAuth
from ..db import get_db
from ..limits import check_lines_limit, TierLimitError, get_tier_limits
from ..models import Kytchen, SandboxSession, Workspace
from .kytchens import _resolve_kytchen, get_auth

if TYPE_CHECKING:
    from ...sandbox import SandboxProvider

router = APIRouter(prefix="/v1/kytchens", tags=["lines"])


def is_dev_mode() -> bool:
    """Check if running in development mode."""
    return os.getenv("KYTCHEN_DEV_MODE", "0").strip() in ("1", "true", "yes")


def _format_line_id(sandbox_id: str) -> str:
    """Format sandbox_id as a line_id."""
    # E2B sandbox IDs are already prefixed with "e2b-", keep them as-is
    if sandbox_id.startswith("e2b-"):
        return f"line_{sandbox_id[4:]}"
    return f"line_{sandbox_id[:12]}"


def _parse_line_id(line_id: str) -> str:
    """Parse line_id back to sandbox_id."""
    if line_id.startswith("line_"):
        return f"e2b-{line_id[5:]}"
    return line_id


# -----------------------------------------------------------------------------
# Request/Response Models
# -----------------------------------------------------------------------------


class LineCreate(BaseModel):
    """Request to create a new Line (sandbox)."""

    config: dict[str, Any] | None = None  # Optional sandbox config overrides
    context_id: str = "default"  # Context identifier within the sandbox


class LineResponse(BaseModel):
    """Response for a Line."""

    id: str
    kytchen_id: str
    e2b_sandbox_id: str
    context_id: str
    status: str
    created_at: datetime
    expires_at: datetime
    metadata: dict[str, Any] | None = None


class LineListResponse(BaseModel):
    """Response for listing Lines."""

    lines: list[LineResponse]
    count: int
    tier_limit: int
    tier_name: str


class ExecRequest(BaseModel):
    """Code execution request."""

    code: str
    timeout_seconds: float = 30.0


class ExecResponse(BaseModel):
    """Code execution response."""

    stdout: str
    stderr: str
    return_value: str | None = None
    error: str | None = None
    execution_time_ms: float
    truncated: bool = False


# -----------------------------------------------------------------------------
# Helper to get or validate kytchen
# -----------------------------------------------------------------------------


async def _get_kytchen_for_lines(
    kytchen_id: str,
    auth: WorkspaceAuth,
    db: AsyncSession,
) -> Kytchen:
    """Get kytchen and verify workspace owns it."""
    return await _resolve_kytchen(
        kytchen_id,
        auth.workspace_id,
        db,
        require_owner=True,
    )


# -----------------------------------------------------------------------------
# Lines CRUD Endpoints
# -----------------------------------------------------------------------------


@router.post("/{kytchen_id}/lines", response_model=LineResponse, status_code=201)
async def create_line(
    kytchen_id: str,
    body: LineCreate,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> LineResponse:
    """Create a new E2B Line (sandbox) for a Kytchen.

    Lines are persistent E2B sandboxes that can execute code in isolation.
    They're tier-limited:
    - Starter: 0 lines (upgrade to use E2B)
    - Chef: 1 line
    - Sous Chef: 3 lines

    The line persists for the E2B timeout duration (default 5 minutes).
    """
    # Verify kytchen exists and belongs to workspace
    kytchen = await _get_kytchen_for_lines(kytchen_id, auth, db)

    # Check tier allows lines
    can_create, current, max_allowed = await check_lines_limit(
        str(auth.workspace_id), db
    )
    if not can_create:
        # Get tier name for error message
        workspace = await db.get(Workspace, auth.workspace_id)
        tier_name = get_tier_limits(workspace.plan)["tier_name"] if workspace else "your"
        raise TierLimitError("E2B Lines", current, max_allowed, tier_name)

    # Import sandbox factory
    from ...sandbox import get_sandbox, SandboxConfig, should_use_e2b

    if not should_use_e2b():
        raise HTTPException(
            status_code=503,
            detail="E2B sandboxes are not available. Check E2B_API_KEY is set.",
        )

    # Build config from defaults + overrides
    config_overrides = body.config or {}
    sandbox_config = SandboxConfig(
        timeout_seconds=config_overrides.get("timeout_seconds", 30.0),
        max_output_chars=config_overrides.get("max_output_chars", 10_000),
        e2b_timeout_seconds=config_overrides.get("e2b_timeout_seconds", 300),
    )

    # Create E2B sandbox
    try:
        sandbox = await get_sandbox(
            workspace_id=str(auth.workspace_id),
            config=sandbox_config,
            force_local=False,  # Always use E2B for Lines
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # IMPORTANT: Lines must persist beyond this request.
    # The E2BSandbox wrapper has a best-effort __del__ that may call kill().
    # Mark it as closed so it won't auto-kill when it goes out of scope.
    try:
        setattr(sandbox, "_closed", True)
    except Exception:
        pass

    # Calculate expiry
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(seconds=sandbox_config.e2b_timeout_seconds)

    # Store in SandboxSession table
    session_record = SandboxSession(
        workspace_id=auth.workspace_id,
        e2b_sandbox_id=sandbox.sandbox_id,
        context_id=body.context_id,
        status="active",
        expires_at=expires_at,
        session_metadata={
            "kytchen_id": str(kytchen.id),
            "config": {
                "timeout_seconds": sandbox_config.timeout_seconds,
                "max_output_chars": sandbox_config.max_output_chars,
                "e2b_timeout_seconds": sandbox_config.e2b_timeout_seconds,
            },
        },
    )
    db.add(session_record)
    await db.commit()
    await db.refresh(session_record)

    return LineResponse(
        id=_format_line_id(sandbox.sandbox_id),
        kytchen_id=kytchen_id,
        e2b_sandbox_id=sandbox.sandbox_id,
        context_id=body.context_id,
        status="active",
        created_at=session_record.created_at,
        expires_at=expires_at,
        metadata=session_record.session_metadata,
    )


@router.get("/{kytchen_id}/lines", response_model=LineListResponse)
async def list_lines(
    kytchen_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> LineListResponse:
    """List all active Lines for a Kytchen.

    Returns only lines that are still active (not expired or closed).
    """
    # Verify kytchen exists and belongs to workspace
    kytchen = await _get_kytchen_for_lines(kytchen_id, auth, db)

    # Get workspace tier info
    workspace = await db.get(Workspace, auth.workspace_id)
    tier_info = get_tier_limits(workspace.plan) if workspace else get_tier_limits(None)

    # Query active lines for this kytchen
    now = datetime.now(timezone.utc)
    query = (
        select(SandboxSession)
        .where(
            SandboxSession.workspace_id == auth.workspace_id,
            SandboxSession.status == "active",
            SandboxSession.expires_at > now,
        )
        .order_by(SandboxSession.created_at.desc())
    )
    result = await db.execute(query)
    sessions = result.scalars().all()

    # Filter to lines belonging to this kytchen
    kytchen_lines = [
        s for s in sessions
        if s.session_metadata.get("kytchen_id") == str(kytchen.id)
    ]

    return LineListResponse(
        lines=[
            LineResponse(
                id=_format_line_id(s.e2b_sandbox_id),
                kytchen_id=kytchen_id,
                e2b_sandbox_id=s.e2b_sandbox_id,
                context_id=s.context_id,
                status=s.status,
                created_at=s.created_at,
                expires_at=s.expires_at,
                metadata=s.session_metadata,
            )
            for s in kytchen_lines
        ],
        count=len(kytchen_lines),
        tier_limit=tier_info["lines"],
        tier_name=tier_info["tier_name"],
    )


@router.get("/{kytchen_id}/lines/{line_id}", response_model=LineResponse)
async def get_line(
    kytchen_id: str,
    line_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> LineResponse:
    """Get details of a specific Line."""
    # Verify kytchen exists and belongs to workspace
    kytchen = await _get_kytchen_for_lines(kytchen_id, auth, db)

    # Parse line_id to sandbox_id
    sandbox_id = _parse_line_id(line_id)

    # Find the session
    result = await db.execute(
        select(SandboxSession).where(
            SandboxSession.workspace_id == auth.workspace_id,
            SandboxSession.e2b_sandbox_id == sandbox_id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Line not found")

    # Verify it belongs to this kytchen
    if session.session_metadata.get("kytchen_id") != str(kytchen.id):
        raise HTTPException(status_code=404, detail="Line not found in this kytchen")

    return LineResponse(
        id=_format_line_id(session.e2b_sandbox_id),
        kytchen_id=kytchen_id,
        e2b_sandbox_id=session.e2b_sandbox_id,
        context_id=session.context_id,
        status=session.status,
        created_at=session.created_at,
        expires_at=session.expires_at,
        metadata=session.session_metadata,
    )


@router.post("/{kytchen_id}/lines/{line_id}/exec", response_model=ExecResponse)
async def execute_in_line(
    kytchen_id: str,
    line_id: str,
    body: ExecRequest,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> ExecResponse:
    """Execute code in an E2B Line.

    The code runs in the isolated E2B sandbox. Helper functions like
    `peek()`, `lines()`, `search()`, `chunk()`, and `cite()` are available.

    Note: Context must be loaded first using /v1/tool/load_context or by
    setting the `ctx` variable directly in code.
    """
    # Verify kytchen exists and belongs to workspace
    kytchen = await _get_kytchen_for_lines(kytchen_id, auth, db)

    # Parse line_id to sandbox_id
    sandbox_id = _parse_line_id(line_id)

    # Find the session
    result = await db.execute(
        select(SandboxSession).where(
            SandboxSession.workspace_id == auth.workspace_id,
            SandboxSession.e2b_sandbox_id == sandbox_id,
            SandboxSession.status == "active",
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Line not found or not active")

    # Verify it belongs to this kytchen
    if session.session_metadata.get("kytchen_id") != str(kytchen.id):
        raise HTTPException(status_code=404, detail="Line not found in this kytchen")

    # Check if expired
    now = datetime.now(timezone.utc)
    if session.expires_at <= now:
        # Mark as expired
        session.status = "expired"
        await db.commit()
        raise HTTPException(status_code=410, detail="Line has expired")

    # Reconnect to the E2B sandbox
    from ...sandbox import SandboxConfig
    from ...sandbox.e2b import E2BSandbox, E2B_AVAILABLE

    if not E2B_AVAILABLE:
        raise HTTPException(status_code=503, detail="E2B SDK not available")

    api_key = os.getenv("E2B_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="E2B_API_KEY not set")

    # Get config from session metadata
    config_data = session.session_metadata.get("config", {})
    config = SandboxConfig(
        timeout_seconds=min(body.timeout_seconds, config_data.get("timeout_seconds", 30.0)),
        max_output_chars=config_data.get("max_output_chars", 10_000),
        e2b_timeout_seconds=config_data.get("e2b_timeout_seconds", 300),
    )

    try:
        # Connect to existing sandbox by ID
        from e2b_code_interpreter import Sandbox as E2BSandboxSDK

        e2b_sandbox = E2BSandboxSDK.connect(
            sandbox_id=sandbox_id,
            api_key=api_key,
        )

        # Execute code
        result = e2b_sandbox.run_code(
            body.code,
            timeout=config.timeout_seconds,
        )

        # Extract outputs
        stdout_parts = []
        stderr_parts = []
        return_value: str | None = None

        for output in result.logs.stdout:
            stdout_parts.append(output)
        for output in result.logs.stderr:
            stderr_parts.append(output)

        if result.results:
            last_result = result.results[-1]
            if hasattr(last_result, 'text'):
                return_value = last_result.text

        error_msg = None
        if result.error:
            error_msg = f"{result.error.name}: {result.error.value}"
            stderr_parts.append(result.error.traceback or "")

        stdout = "\n".join(stdout_parts)
        stderr = "\n".join(stderr_parts)

        # Truncate if needed
        truncated = False
        if len(stdout) > config.max_output_chars:
            stdout = stdout[:config.max_output_chars] + "\n... [OUTPUT TRUNCATED]"
            truncated = True
        if len(stderr) > config.max_output_chars:
            stderr = stderr[:config.max_output_chars] + "\n... [OUTPUT TRUNCATED]"
            truncated = True

        return ExecResponse(
            stdout=stdout,
            stderr=stderr,
            return_value=return_value,
            error=error_msg,
            execution_time_ms=0.0,  # E2B doesn't expose this directly
            truncated=truncated,
        )

    except Exception as e:
        error_str = str(e)
        # Check if sandbox no longer exists
        if "not found" in error_str.lower() or "does not exist" in error_str.lower():
            session.status = "expired"
            await db.commit()
            raise HTTPException(status_code=410, detail="Line has expired or was terminated")
        raise HTTPException(status_code=500, detail=f"Execution failed: {error_str}")


@router.delete("/{kytchen_id}/lines/{line_id}", status_code=204)
async def delete_line(
    kytchen_id: str,
    line_id: str,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Destroy an E2B Line.

    This terminates the E2B sandbox and removes the session record.
    The sandbox will stop incurring charges immediately.
    """
    # Verify kytchen exists and belongs to workspace
    kytchen = await _get_kytchen_for_lines(kytchen_id, auth, db)

    # Parse line_id to sandbox_id
    sandbox_id = _parse_line_id(line_id)

    # Find the session
    result = await db.execute(
        select(SandboxSession).where(
            SandboxSession.workspace_id == auth.workspace_id,
            SandboxSession.e2b_sandbox_id == sandbox_id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Line not found")

    # Verify it belongs to this kytchen
    if session.session_metadata.get("kytchen_id") != str(kytchen.id):
        raise HTTPException(status_code=404, detail="Line not found in this kytchen")

    # Try to kill the E2B sandbox
    api_key = os.getenv("E2B_API_KEY")
    if api_key and session.status == "active":
        try:
            from e2b_code_interpreter import Sandbox as E2BSandboxSDK

            e2b_sandbox = E2BSandboxSDK.connect(
                sandbox_id=sandbox_id,
                api_key=api_key,
            )
            e2b_sandbox.kill()
        except Exception:
            # Sandbox might already be dead, that's fine
            pass

    # Delete the session record
    await db.delete(session)
    await db.commit()


# -----------------------------------------------------------------------------
# Context Management (convenience endpoints)
# -----------------------------------------------------------------------------


class LoadContextRequest(BaseModel):
    """Request to load context into a Line."""

    context: str
    var_name: str = "ctx"


class LoadContextResponse(BaseModel):
    """Response after loading context."""

    loaded: bool
    size_chars: int
    size_lines: int
    var_name: str


@router.post("/{kytchen_id}/lines/{line_id}/context", response_model=LoadContextResponse)
async def load_context_to_line(
    kytchen_id: str,
    line_id: str,
    body: LoadContextRequest,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> LoadContextResponse:
    """Load context into a Line's sandbox.

    This sets the specified variable (default: `ctx`) in the sandbox
    to the provided context string. Helper functions will then operate
    on this context.
    """
    # Verify kytchen exists and belongs to workspace
    kytchen = await _get_kytchen_for_lines(kytchen_id, auth, db)

    # Parse line_id to sandbox_id
    sandbox_id = _parse_line_id(line_id)

    # Find the session
    result = await db.execute(
        select(SandboxSession).where(
            SandboxSession.workspace_id == auth.workspace_id,
            SandboxSession.e2b_sandbox_id == sandbox_id,
            SandboxSession.status == "active",
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Line not found or not active")

    # Verify it belongs to this kytchen
    if session.session_metadata.get("kytchen_id") != str(kytchen.id):
        raise HTTPException(status_code=404, detail="Line not found in this kytchen")

    # Check if expired
    now = datetime.now(timezone.utc)
    if session.expires_at <= now:
        session.status = "expired"
        await db.commit()
        raise HTTPException(status_code=410, detail="Line has expired")

    # Connect to E2B sandbox and load context
    api_key = os.getenv("E2B_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="E2B_API_KEY not set")

    try:
        from e2b_code_interpreter import Sandbox as E2BSandboxSDK
        import json

        e2b_sandbox = E2BSandboxSDK.connect(
            sandbox_id=sandbox_id,
            api_key=api_key,
        )

        # Load context by setting variable
        context_repr = repr(body.context)
        code = f"{body.var_name} = {context_repr}"
        e2b_sandbox.run_code(code)

        return LoadContextResponse(
            loaded=True,
            size_chars=len(body.context),
            size_lines=body.context.count("\n") + 1,
            var_name=body.var_name,
        )

    except Exception as e:
        error_str = str(e)
        if "not found" in error_str.lower() or "does not exist" in error_str.lower():
            session.status = "expired"
            await db.commit()
            raise HTTPException(status_code=410, detail="Line has expired or was terminated")
        raise HTTPException(status_code=500, detail=f"Failed to load context: {error_str}")

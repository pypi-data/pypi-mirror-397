"""State backends for Kytchen Cloud.

Provides both in-memory (for development) and PostgreSQL-backed (for production)
implementations of storage, rate limiting, and usage tracking.
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Deque, Literal

try:
    from sqlalchemy import delete as sql_delete
    from sqlalchemy import select, update
    from sqlalchemy.ext.asyncio import AsyncSession
except Exception:  # pragma: no cover
    select = None  # type: ignore[assignment]
    update = None  # type: ignore[assignment]
    sql_delete = None  # type: ignore[assignment]
    AsyncSession = Any  # type: ignore[assignment]

from ..repl.sandbox import REPLEnvironment
from ..sandbox import SandboxProvider
from ..types import ContextMetadata


@dataclass(frozen=True, slots=True)
class DatasetRecord:
    id: str
    name: str
    size_bytes: int
    content_hash: str
    mime_type: str | None
    created_at: float
    status: Literal["uploaded", "processing", "ready", "failed"] = "ready"
    processing_error: str | None = None


@dataclass
class EvidenceRecord:
    tool_name: str
    params: dict[str, Any]
    snippet: str
    line_range: tuple[int, int] | None
    note: str | None
    created_at: float = field(default_factory=time.time)


@dataclass
class RunRecord:
    id: str
    query: str
    status: Literal["queued", "running", "completed", "failed"] = "running"
    tool_session_id: str | None = None
    kytchen_id: str | None = None
    dataset_ids: list[str] = field(default_factory=list)
    budget: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    answer: str | None = None
    success: bool | None = None
    error: str | None = None
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None


@dataclass
class ToolSession:
    """Session state for tool execution.

    Supports both local REPLEnvironment and remote SandboxProvider backends.
    The sandbox field is the preferred abstraction; repl is kept for backwards
    compatibility but should be migrated to sandbox.
    """
    repl: REPLEnvironment | None = None  # Deprecated, use sandbox
    sandbox: SandboxProvider | None = None  # Preferred abstraction
    meta: ContextMetadata | None = None
    sandbox_id: str | None = None  # E2B sandbox ID for tracking
    created_at: float = field(default_factory=time.time)
    iterations: int = 0
    think_history: list[str] = field(default_factory=list)
    evidence: list[EvidenceRecord] = field(default_factory=list)
    confidence_history: list[float] = field(default_factory=list)
    chunks: list[dict[str, int]] | None = None
    finalized_answer: str | None = None

    def get_variable(self, name: str) -> object | None:
        """Get variable from sandbox (supports both backends)."""
        if self.sandbox is not None:
            # For async sandbox, we need to handle this differently
            # For now, fall back to repl if available
            pass
        if self.repl is not None:
            return self.repl.get_variable(name)
        return None


class MemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, key: str, limit_per_min: int) -> None:
        now = time.time()
        cutoff = now - 60.0
        async with self._lock:
            q = self._hits[key]
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= limit_per_min:
                raise RuntimeError("rate_limit")
            q.append(now)


class MemoryUsageTracker:
    def __init__(self) -> None:
        self._storage_bytes: dict[str, int] = defaultdict(int)
        self._egress_bytes: dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def storage_used(self, workspace_id: str) -> int:
        async with self._lock:
            return int(self._storage_bytes[workspace_id])

    async def add_storage(self, workspace_id: str, add_bytes: int) -> None:
        async with self._lock:
            self._storage_bytes[workspace_id] += int(add_bytes)

    async def sub_storage(self, workspace_id: str, sub_bytes: int) -> None:
        async with self._lock:
            self._storage_bytes[workspace_id] = max(0, self._storage_bytes[workspace_id] - int(sub_bytes))

    async def add_egress_or_reject(self, workspace_id: str, add_bytes: int, limit_bytes: int) -> None:
        async with self._lock:
            if self._egress_bytes[workspace_id] + int(add_bytes) > int(limit_bytes):
                raise RuntimeError("egress_limit")
            self._egress_bytes[workspace_id] += int(add_bytes)


class MemoryStore:
    def __init__(self) -> None:
        self._datasets: dict[str, dict[str, DatasetRecord]] = defaultdict(dict)  # ws -> id -> record
        self._dataset_bytes: dict[str, dict[str, bytes]] = defaultdict(dict)
        self._runs: dict[str, dict[str, RunRecord]] = defaultdict(dict)
        self._sessions: dict[str, dict[str, ToolSession]] = defaultdict(dict)  # ws -> context_id -> session
        self._lock = asyncio.Lock()

    async def create_dataset(
        self,
        workspace_id: str,
        *,
        name: str,
        content: bytes,
        content_hash: str,
        mime_type: str | None,
        status: Literal["uploaded", "processing", "ready", "failed"] = "uploaded",
    ) -> DatasetRecord:
        ds_id = str(uuid.uuid4())
        rec = DatasetRecord(
            id=ds_id,
            name=name,
            size_bytes=len(content),
            content_hash=content_hash,
            mime_type=mime_type,
            created_at=time.time(),
            status=status,
        )
        async with self._lock:
            self._datasets[workspace_id][ds_id] = rec
            self._dataset_bytes[workspace_id][ds_id] = content
        return rec

    async def list_datasets(self, workspace_id: str) -> list[DatasetRecord]:
        async with self._lock:
            return list(self._datasets[workspace_id].values())

    async def get_dataset(self, workspace_id: str, dataset_id: str) -> DatasetRecord | None:
        async with self._lock:
            return self._datasets[workspace_id].get(dataset_id)

    async def delete_dataset(self, workspace_id: str, dataset_id: str) -> DatasetRecord | None:
        async with self._lock:
            rec = self._datasets[workspace_id].pop(dataset_id, None)
            self._dataset_bytes[workspace_id].pop(dataset_id, None)
            return rec

    async def create_run(
        self,
        workspace_id: str,
        *,
        query: str,
        kytchen_id: str | None = None,
        dataset_ids: list[str] | None = None,
        budget: dict | None = None,
    ) -> RunRecord:
        run_id = str(uuid.uuid4())
        rec = RunRecord(
            id=run_id,
            query=query,
            tool_session_id=run_id,
            kytchen_id=kytchen_id,
            dataset_ids=dataset_ids or [],
            budget=budget or {},
        )
        async with self._lock:
            self._runs[workspace_id][run_id] = rec
        return rec

    async def get_run(self, workspace_id: str, run_id: str) -> RunRecord | None:
        async with self._lock:
            return self._runs[workspace_id].get(run_id)

    async def upsert_session(self, workspace_id: str, context_id: str, session: ToolSession) -> None:
        async with self._lock:
            self._sessions[workspace_id][context_id] = session

    async def get_session(self, workspace_id: str, context_id: str) -> ToolSession | None:
        async with self._lock:
            return self._sessions[workspace_id].get(context_id)


# -----------------------------------------------------------------------------
# PostgreSQL-backed implementations
# -----------------------------------------------------------------------------


class PostgresStore:
    """PostgreSQL-backed storage for datasets and runs.

    This replaces MemoryStore for production deployments on Replit.
    Dataset content is stored in App Storage, metadata in PostgreSQL.
    """

    def __init__(self, db: AsyncSession, storage: Any) -> None:
        """Initialize PostgreSQL store.

        Args:
            db: SQLAlchemy async session
            storage: ReplitStorage instance for file operations
        """
        self.db = db
        self.storage = storage

    async def create_dataset(
        self,
        workspace_id: str,
        *,
        name: str,
        content: bytes,
        content_hash: str,
        mime_type: str | None,
        status: Literal["uploaded", "processing", "ready", "failed"] = "uploaded",
    ) -> DatasetRecord:
        """Create a new dataset.

        Args:
            workspace_id: UUID of the workspace
            name: Dataset name
            content: Binary content
            content_hash: SHA256 hash with prefix
            mime_type: MIME type (optional)
            status: Initial status (default: 'uploaded' for processing pipeline)

        Returns:
            DatasetRecord with metadata
        """
        from .models import Dataset, DatasetStatus

        ds_id = str(uuid.uuid4())

        # Write content to storage
        storage_path = await self.storage.write_dataset(workspace_id, ds_id, content)

        # Map string status to enum
        status_enum = DatasetStatus(status)

        # Create database record
        dataset = Dataset(
            id=ds_id,
            workspace_id=workspace_id,
            name=name,
            storage_bucket="pantry",
            storage_path=storage_path,
            size_bytes=len(content),
            content_hash=content_hash,
            mime_type=mime_type,
            status=status_enum,
        )

        self.db.add(dataset)
        await self.db.flush()

        return DatasetRecord(
            id=str(dataset.id),
            name=dataset.name,
            size_bytes=dataset.size_bytes,
            content_hash=dataset.content_hash,
            mime_type=dataset.mime_type,
            created_at=dataset.created_at.timestamp(),
            status=dataset.status.value,
        )

    async def list_datasets(self, workspace_id: str) -> list[DatasetRecord]:
        """List all datasets in a workspace.

        Args:
            workspace_id: UUID of the workspace

        Returns:
            List of DatasetRecords
        """
        from .models import Dataset

        result = await self.db.execute(
            select(Dataset)
            .where(Dataset.workspace_id == workspace_id)
            .order_by(Dataset.created_at.desc())
        )
        datasets = result.scalars().all()

        return [
            DatasetRecord(
                id=str(ds.id),
                name=ds.name,
                size_bytes=ds.size_bytes,
                content_hash=ds.content_hash,
                mime_type=ds.mime_type,
                created_at=ds.created_at.timestamp(),
                status=ds.status.value,
                processing_error=ds.processing_error,
            )
            for ds in datasets
        ]

    async def get_dataset(self, workspace_id: str, dataset_id: str) -> DatasetRecord | None:
        """Get a dataset by ID.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset

        Returns:
            DatasetRecord or None if not found
        """
        from .models import Dataset

        result = await self.db.execute(
            select(Dataset).where(
                Dataset.workspace_id == workspace_id,
                Dataset.id == dataset_id,
            )
        )
        dataset = result.scalar_one_or_none()

        if dataset is None:
            return None

        return DatasetRecord(
            id=str(dataset.id),
            name=dataset.name,
            size_bytes=dataset.size_bytes,
            content_hash=dataset.content_hash,
            mime_type=dataset.mime_type,
            created_at=dataset.created_at.timestamp(),
            status=dataset.status.value,
            processing_error=dataset.processing_error,
        )

    async def delete_dataset(self, workspace_id: str, dataset_id: str) -> DatasetRecord | None:
        """Delete a dataset.

        Args:
            workspace_id: UUID of the workspace
            dataset_id: UUID of the dataset

        Returns:
            DatasetRecord if deleted, None if not found
        """
        from .models import Dataset

        # Get dataset first
        rec = await self.get_dataset(workspace_id, dataset_id)
        if rec is None:
            return None

        # Delete from storage
        await self.storage.delete_dataset(workspace_id, dataset_id)

        # Delete from database
        await self.db.execute(
            sql_delete(Dataset).where(
                Dataset.workspace_id == workspace_id,
                Dataset.id == dataset_id,
            )
        )

        return rec

    async def create_run(
        self,
        workspace_id: str,
        *,
        query: str,
        kytchen_id: str | None = None,
        dataset_ids: list[str] | None = None,
        budget: dict | None = None,
    ) -> RunRecord:
        """Create a new run.

        Args:
            workspace_id: UUID of the workspace
            query: User query
            kitchen_id: UUID of the kitchen (optional)
            dataset_ids: List of dataset UUIDs used
            budget: Budget configuration

        Returns:
            RunRecord with metadata
        """
        from .models import Run, RunStatus

        run_id = str(uuid.uuid4())

        run = Run(
            id=run_id,
            workspace_id=workspace_id,
            kytchen_id=kytchen_id,
            query=query,
            dataset_ids=dataset_ids or [],
            budget=budget or {},
            status=RunStatus.running,
            tool_session_id=run_id,
        )

        self.db.add(run)
        await self.db.flush()

        return RunRecord(
            id=str(run.id),
            query=run.query,
            status=run.status.value,
            tool_session_id=run.tool_session_id,
            kytchen_id=str(run.kytchen_id) if run.kytchen_id else None,
            dataset_ids=[str(d) for d in run.dataset_ids] if run.dataset_ids else [],
            budget=run.budget or {},
            metrics=run.metrics or {},
            created_at=run.created_at.timestamp(),
        )

    async def get_run(self, workspace_id: str, run_id: str) -> RunRecord | None:
        """Get a run by ID.

        Args:
            workspace_id: UUID of the workspace
            run_id: UUID of the run

        Returns:
            RunRecord or None if not found
        """
        from .models import Run

        result = await self.db.execute(
            select(Run).where(
                Run.workspace_id == workspace_id,
                Run.id == run_id,
            )
        )
        run = result.scalar_one_or_none()

        if run is None:
            return None

        return RunRecord(
            id=str(run.id),
            query=run.query,
            status=run.status.value,
            tool_session_id=run.tool_session_id,
            kytchen_id=str(run.kytchen_id) if run.kytchen_id else None,
            dataset_ids=[str(d) for d in run.dataset_ids] if run.dataset_ids else [],
            budget=run.budget or {},
            metrics=run.metrics or {},
            answer=run.answer,
            success=run.success,
            error=run.error,
            created_at=run.created_at.timestamp(),
            completed_at=run.completed_at.timestamp() if run.completed_at else None,
        )

    async def update_run(
        self,
        workspace_id: str,
        run_id: str,
        *,
        answer: str | None = None,
        success: bool | None = None,
        error: str | None = None,
        status: str | None = None,
        metrics: dict | None = None,
    ) -> RunRecord | None:
        """Update a run.

        Args:
            workspace_id: UUID of the workspace
            run_id: UUID of the run
            answer: Final answer
            success: Success status
            error: Error message
            status: Run status
            metrics: Execution metrics (tokens, cost, etc.)

        Returns:
            Updated RunRecord or None if not found
        """
        from .models import Run, RunStatus

        updates = {}
        if answer is not None:
            updates["answer"] = answer
        if success is not None:
            updates["success"] = success
        if error is not None:
            updates["error"] = error
        if metrics is not None:
            updates["metrics"] = metrics
        if status is not None:
            updates["status"] = RunStatus(status)
            if status in ("completed", "failed", "canceled"):
                updates["completed_at"] = datetime.now(timezone.utc)

        if not updates:
            return await self.get_run(workspace_id, run_id)

        await self.db.execute(
            update(Run)
            .where(Run.workspace_id == workspace_id, Run.id == run_id)
            .values(**updates)
        )

        return await self.get_run(workspace_id, run_id)

    # Session management (still in-memory for now - could be Redis/Valkey)
    _sessions: dict[str, dict[str, ToolSession]] = {}
    _lock = asyncio.Lock()

    async def upsert_session(self, workspace_id: str, context_id: str, session: ToolSession) -> None:
        """Store a tool session (in-memory for now).

        Args:
            workspace_id: UUID of the workspace
            context_id: Session context ID
            session: ToolSession instance
        """
        async with self._lock:
            if workspace_id not in self._sessions:
                self._sessions[workspace_id] = {}
            self._sessions[workspace_id][context_id] = session

    async def get_session(self, workspace_id: str, context_id: str) -> ToolSession | None:
        """Get a tool session.

        Args:
            workspace_id: UUID of the workspace
            context_id: Session context ID

        Returns:
            ToolSession or None if not found
        """
        async with self._lock:
            return self._sessions.get(workspace_id, {}).get(context_id)


class PostgresUsageTracker:
    """PostgreSQL-backed usage tracking for workspace limits."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize usage tracker.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def _ensure_usage_record(self, workspace_id: str) -> None:
        """Ensure usage record exists for workspace.

        Args:
            workspace_id: UUID of the workspace
        """
        from .models import Usage

        result = await self.db.execute(
            select(Usage).where(Usage.workspace_id == workspace_id)
        )
        usage = result.scalar_one_or_none()

        if usage is None:
            usage = Usage(workspace_id=workspace_id)
            self.db.add(usage)
            await self.db.flush()

    async def storage_used(self, workspace_id: str) -> int:
        """Get storage usage for workspace.

        Args:
            workspace_id: UUID of the workspace

        Returns:
            Storage in bytes
        """
        from .models import Usage

        await self._ensure_usage_record(workspace_id)

        result = await self.db.execute(
            select(Usage.storage_bytes).where(Usage.workspace_id == workspace_id)
        )
        return result.scalar_one() or 0

    async def add_storage(self, workspace_id: str, add_bytes: int) -> None:
        """Add storage usage.

        Args:
            workspace_id: UUID of the workspace
            add_bytes: Bytes to add
        """
        from .models import Usage

        await self._ensure_usage_record(workspace_id)

        await self.db.execute(
            update(Usage)
            .where(Usage.workspace_id == workspace_id)
            .values(storage_bytes=Usage.storage_bytes + add_bytes)
        )

    async def sub_storage(self, workspace_id: str, sub_bytes: int) -> None:
        """Subtract storage usage.

        Args:
            workspace_id: UUID of the workspace
            sub_bytes: Bytes to subtract
        """
        from .models import Usage

        await self._ensure_usage_record(workspace_id)

        await self.db.execute(
            update(Usage)
            .where(Usage.workspace_id == workspace_id)
            .values(storage_bytes=Usage.storage_bytes - sub_bytes)
        )

    async def add_egress_or_reject(self, workspace_id: str, add_bytes: int, limit_bytes: int) -> None:
        """Add egress usage or reject if limit exceeded.

        Args:
            workspace_id: UUID of the workspace
            add_bytes: Bytes to add
            limit_bytes: Maximum allowed bytes

        Raises:
            RuntimeError: If limit would be exceeded
        """
        from .models import Usage

        await self._ensure_usage_record(workspace_id)

        result = await self.db.execute(
            select(Usage.egress_bytes_this_month).where(Usage.workspace_id == workspace_id)
        )
        current = result.scalar_one() or 0

        if current + add_bytes > limit_bytes:
            raise RuntimeError("egress_limit")

        await self.db.execute(
            update(Usage)
            .where(Usage.workspace_id == workspace_id)
            .values(egress_bytes_this_month=Usage.egress_bytes_this_month + add_bytes)
        )


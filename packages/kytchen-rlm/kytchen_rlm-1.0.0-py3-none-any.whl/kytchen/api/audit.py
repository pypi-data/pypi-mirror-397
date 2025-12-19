"""Audit logging for Kytchen Cloud.

Provides immutable, tamper-evident audit logging for compliance requirements.
All significant actions are logged with:
- Event classification (type, category, severity)
- Actor identification (user, API key, or system)
- Resource tracking (what was affected)
- Hash chain for tamper detection

Usage:
    from kytchen.api.audit import AuditLogger, EventType, EventCategory

    logger = AuditLogger(db_session)
    await logger.log(
        workspace_id=workspace_id,
        event_type=EventType.RUN_STARTED,
        actor_type="api_key",
        actor_id=api_key_id,
        resource_type="run",
        resource_id=run_id,
        description="Query execution started",
        metadata={"query_preview": query[:100]},
    )
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

try:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession
except Exception:  # pragma: no cover
    text = None  # type: ignore[assignment]
    AsyncSession = Any  # type: ignore[assignment]


class EventType(str, Enum):
    """Audit event types."""
    # Run lifecycle
    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"

    # Dataset operations
    DATASET_UPLOADED = "dataset.uploaded"
    DATASET_DELETED = "dataset.deleted"
    DATASET_PROCESSED = "dataset.processed"

    # API key operations
    KEY_CREATED = "key.created"
    KEY_ROTATED = "key.rotated"
    KEY_REVOKED = "key.revoked"

    # Workspace operations
    WORKSPACE_CREATED = "workspace.created"
    WORKSPACE_SETTINGS_CHANGED = "workspace.settings_changed"
    MEMBER_ADDED = "member.added"
    MEMBER_REMOVED = "member.removed"

    # Evidence operations
    EVIDENCE_EXPORTED = "evidence.exported"

    # Sandbox operations
    SANDBOX_CREATED = "sandbox.created"
    SANDBOX_TERMINATED = "sandbox.terminated"

    # Billing operations
    PLAN_CHANGED = "plan.changed"
    PAYMENT_SUCCEEDED = "payment.succeeded"
    PAYMENT_FAILED = "payment.failed"

    # Security events
    AUTH_FAILED = "auth.failed"
    RATE_LIMITED = "rate.limited"


class EventCategory(str, Enum):
    """Event categories for filtering."""
    DATA = "data"      # Dataset operations
    AUTH = "auth"      # Authentication, key management
    ADMIN = "admin"    # Workspace settings
    SYSTEM = "system"  # Internal operations
    BILLING = "billing"  # Payment and plan changes
    SECURITY = "security"  # Security events


class EventSeverity(str, Enum):
    """Event severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# Map event types to categories
EVENT_CATEGORY_MAP: dict[EventType, EventCategory] = {
    EventType.RUN_STARTED: EventCategory.DATA,
    EventType.RUN_COMPLETED: EventCategory.DATA,
    EventType.RUN_FAILED: EventCategory.DATA,
    EventType.DATASET_UPLOADED: EventCategory.DATA,
    EventType.DATASET_DELETED: EventCategory.DATA,
    EventType.DATASET_PROCESSED: EventCategory.DATA,
    EventType.KEY_CREATED: EventCategory.AUTH,
    EventType.KEY_ROTATED: EventCategory.AUTH,
    EventType.KEY_REVOKED: EventCategory.AUTH,
    EventType.WORKSPACE_CREATED: EventCategory.ADMIN,
    EventType.WORKSPACE_SETTINGS_CHANGED: EventCategory.ADMIN,
    EventType.MEMBER_ADDED: EventCategory.ADMIN,
    EventType.MEMBER_REMOVED: EventCategory.ADMIN,
    EventType.EVIDENCE_EXPORTED: EventCategory.DATA,
    EventType.SANDBOX_CREATED: EventCategory.SYSTEM,
    EventType.SANDBOX_TERMINATED: EventCategory.SYSTEM,
    EventType.PLAN_CHANGED: EventCategory.BILLING,
    EventType.PAYMENT_SUCCEEDED: EventCategory.BILLING,
    EventType.PAYMENT_FAILED: EventCategory.BILLING,
    EventType.AUTH_FAILED: EventCategory.SECURITY,
    EventType.RATE_LIMITED: EventCategory.SECURITY,
}


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """Immutable audit event record."""
    workspace_id: str
    event_type: EventType
    event_category: EventCategory
    severity: EventSeverity
    actor_type: str  # 'user', 'api_key', 'system'
    actor_id: str | None
    actor_ip: str | None
    user_agent: str | None
    resource_type: str | None
    resource_id: str | None
    description: str
    metadata: dict[str, Any]
    content_hash: str
    previous_hash: str | None
    created_at: datetime


def compute_event_hash(
    workspace_id: str,
    event_type: str,
    description: str,
    metadata: dict[str, Any],
    previous_hash: str | None,
    timestamp: datetime,
) -> str:
    """Compute SHA-256 hash for immutability chain.

    The hash includes:
    - workspace_id
    - event_type
    - description
    - metadata
    - previous_hash (chain link)
    - timestamp

    This creates a tamper-evident chain where modifying any event
    would break the hash chain.
    """
    payload = {
        "workspace_id": workspace_id,
        "event_type": event_type,
        "description": description,
        "metadata": metadata,
        "previous_hash": previous_hash,
        "timestamp": timestamp.isoformat(),
    }
    content = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class AuditLogger:
    """Audit logger for Kytchen Cloud.

    Handles logging audit events to the database with hash chain
    for tamper detection.
    """

    def __init__(self, db: AsyncSession):
        if text is None:
            raise RuntimeError("SQLAlchemy is required for AuditLogger. Install `pip install 'kytchen[api]'`.")
        self.db = db
        """Initialize audit logger.

        Args:
            db: Async database session
        """
        self._db = db
        self._previous_hash_cache: dict[str, str | None] = {}

    async def _get_previous_hash(self, workspace_id: str) -> str | None:
        """Get the hash of the most recent audit log entry for a workspace."""
        # Check cache first
        if workspace_id in self._previous_hash_cache:
            return self._previous_hash_cache[workspace_id]

        result = await self._db.execute(
            text("""
                SELECT content_hash FROM public.audit_logs
                WHERE workspace_id = :workspace_id
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"workspace_id": workspace_id},
        )
        row = result.fetchone()
        previous_hash = row[0] if row else None
        self._previous_hash_cache[workspace_id] = previous_hash
        return previous_hash

    async def log(
        self,
        workspace_id: str,
        event_type: EventType,
        actor_type: str,
        description: str,
        actor_id: str | None = None,
        actor_ip: str | None = None,
        user_agent: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        severity: EventSeverity | None = None,
    ) -> AuditEvent:
        """Log an audit event.

        Args:
            workspace_id: Workspace ID
            event_type: Type of event
            actor_type: 'user', 'api_key', or 'system'
            description: Human-readable description
            actor_id: ID of the actor (user_id, api_key_id)
            actor_ip: Source IP address
            user_agent: Request user agent
            resource_type: Type of affected resource
            resource_id: ID of affected resource
            metadata: Additional structured data
            severity: Event severity (defaults based on event type)

        Returns:
            The created AuditEvent
        """
        metadata = metadata or {}
        now = datetime.now(timezone.utc)

        # Determine category from event type
        event_category = EVENT_CATEGORY_MAP.get(event_type, EventCategory.SYSTEM)

        # Default severity based on event type
        if severity is None:
            if event_type in (EventType.RUN_FAILED, EventType.PAYMENT_FAILED):
                severity = EventSeverity.ERROR
            elif event_type in (EventType.AUTH_FAILED, EventType.RATE_LIMITED):
                severity = EventSeverity.WARNING
            else:
                severity = EventSeverity.INFO

        # Get previous hash for chain
        previous_hash = await self._get_previous_hash(workspace_id)

        # Compute content hash
        content_hash = compute_event_hash(
            workspace_id=workspace_id,
            event_type=event_type.value,
            description=description,
            metadata=metadata,
            previous_hash=previous_hash,
            timestamp=now,
        )

        # Insert into database
        await self._db.execute(
            text("""
                INSERT INTO public.audit_logs (
                    workspace_id, event_type, event_category, severity,
                    actor_type, actor_id, actor_ip, user_agent,
                    resource_type, resource_id, description, metadata,
                    content_hash, previous_hash, created_at
                ) VALUES (
                    :workspace_id, :event_type, :event_category, :severity,
                    :actor_type, :actor_id, :actor_ip, :user_agent,
                    :resource_type, :resource_id, :description, :metadata,
                    :content_hash, :previous_hash, :created_at
                )
            """),
            {
                "workspace_id": workspace_id,
                "event_type": event_type.value,
                "event_category": event_category.value,
                "severity": severity.value,
                "actor_type": actor_type,
                "actor_id": actor_id,
                "actor_ip": actor_ip,
                "user_agent": user_agent,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "description": description,
                "metadata": json.dumps(metadata),
                "content_hash": content_hash,
                "previous_hash": previous_hash,
                "created_at": now,
            },
        )
        await self._db.commit()

        # Update cache
        self._previous_hash_cache[workspace_id] = content_hash

        return AuditEvent(
            workspace_id=workspace_id,
            event_type=event_type,
            event_category=event_category,
            severity=severity,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_ip=actor_ip,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            metadata=metadata,
            content_hash=content_hash,
            previous_hash=previous_hash,
            created_at=now,
        )

    async def verify_chain(self, workspace_id: str) -> tuple[bool, list[str]]:
        """Verify the hash chain for a workspace's audit logs.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        result = await self._db.execute(
            text("""
                SELECT id, event_type, description, metadata,
                       content_hash, previous_hash, created_at
                FROM public.audit_logs
                WHERE workspace_id = :workspace_id
                ORDER BY created_at ASC
            """),
            {"workspace_id": workspace_id},
        )
        rows = result.fetchall()

        errors: list[str] = []
        expected_previous: str | None = None

        for row in rows:
            log_id, event_type, description, metadata_json, content_hash, previous_hash, created_at = row

            # Verify previous hash matches
            if previous_hash != expected_previous:
                errors.append(
                    f"Chain broken at {log_id}: expected previous_hash={expected_previous}, got {previous_hash}"
                )

            # Verify content hash
            metadata = json.loads(metadata_json) if metadata_json else {}
            expected_hash = compute_event_hash(
                workspace_id=workspace_id,
                event_type=event_type,
                description=description,
                metadata=metadata,
                previous_hash=previous_hash,
                timestamp=created_at,
            )
            if content_hash != expected_hash:
                errors.append(
                    f"Content hash mismatch at {log_id}: expected {expected_hash}, got {content_hash}"
                )

            expected_previous = content_hash

        return len(errors) == 0, errors


class MemoryAuditLogger:
    """In-memory audit logger for development/testing."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []
        self._previous_hash: dict[str, str | None] = {}

    async def log(
        self,
        workspace_id: str,
        event_type: EventType,
        actor_type: str,
        description: str,
        actor_id: str | None = None,
        actor_ip: str | None = None,
        user_agent: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        severity: EventSeverity | None = None,
    ) -> AuditEvent:
        """Log an audit event to memory."""
        metadata = metadata or {}
        now = datetime.now(timezone.utc)

        event_category = EVENT_CATEGORY_MAP.get(event_type, EventCategory.SYSTEM)

        if severity is None:
            if event_type in (EventType.RUN_FAILED, EventType.PAYMENT_FAILED):
                severity = EventSeverity.ERROR
            elif event_type in (EventType.AUTH_FAILED, EventType.RATE_LIMITED):
                severity = EventSeverity.WARNING
            else:
                severity = EventSeverity.INFO

        previous_hash = self._previous_hash.get(workspace_id)

        content_hash = compute_event_hash(
            workspace_id=workspace_id,
            event_type=event_type.value,
            description=description,
            metadata=metadata,
            previous_hash=previous_hash,
            timestamp=now,
        )

        event = AuditEvent(
            workspace_id=workspace_id,
            event_type=event_type,
            event_category=event_category,
            severity=severity,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_ip=actor_ip,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            metadata=metadata,
            content_hash=content_hash,
            previous_hash=previous_hash,
            created_at=now,
        )

        self._events.append(event)
        self._previous_hash[workspace_id] = content_hash
        return event

    def get_events(self, workspace_id: str | None = None) -> list[AuditEvent]:
        """Get audit events, optionally filtered by workspace."""
        if workspace_id is None:
            return list(self._events)
        return [e for e in self._events if e.workspace_id == workspace_id]

    def clear(self) -> None:
        """Clear all events."""
        self._events.clear()
        self._previous_hash.clear()

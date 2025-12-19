"""SQLAlchemy models for Kytchen Cloud on Replit.

These models mirror the Supabase schema from 001_initial_kytchen.sql but adapted
for application-level access control (Replit doesn't have built-in RLS).

Key differences from Supabase:
- Added `users` table (replaces auth.users)
- No RLS policies (enforced in Python application layer)
- No PostgreSQL-specific extensions (pgcrypto)
- JSONB columns for flexibility (budget, params)
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base, GUID, UUIDArray


# -----------------------------------------------------------------------------
# Enums
# -----------------------------------------------------------------------------


class WorkspacePlan(str, enum.Enum):
    """Workspace billing plan."""
    free = "free"
    pro = "pro"
    team = "team"


class MemberRole(str, enum.Enum):
    """Member role within a workspace."""
    owner = "owner"
    admin = "admin"
    member = "member"


class DatasetStatus(str, enum.Enum):
    """Dataset processing status."""
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class RunStatus(str, enum.Enum):
    """Run execution status."""
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


# -----------------------------------------------------------------------------
# Models
# -----------------------------------------------------------------------------


class User(Base):
    """User accounts (replaces Supabase auth.users).

    In Replit, we authenticate via OIDC and store user info here.
    """
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    replit_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    memberships: Mapped[List["Member"]] = relationship(
        "Member",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Workspace(Base):
    """Workspaces for organizing datasets and runs."""
    __tablename__ = "workspaces"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    plan: Mapped[WorkspacePlan] = mapped_column(
        Enum(WorkspacePlan, native_enum=False),
        nullable=False,
        default=WorkspacePlan.free,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    members: Mapped[List["Member"]] = relationship(
        "Member",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    api_keys: Mapped[List["APIKey"]] = relationship(
        "APIKey",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    runs: Mapped[List["Run"]] = relationship(
        "Run",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    evidence: Mapped[List["Evidence"]] = relationship(
        "Evidence",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    usage: Mapped["Usage | None"] = relationship(
        "Usage",
        back_populates="workspace",
        uselist=False,
        cascade="all, delete-orphan",
    )
    kytchens: Mapped[List["Kytchen"]] = relationship(
        "Kytchen",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )


class Member(Base):
    """Workspace membership (many-to-many: users <-> workspaces)."""
    __tablename__ = "members"

    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, native_enum=False),
        nullable=False,
        default=MemberRole.member,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="memberships")


class APIKey(Base):
    """API keys for MCP client authentication (kyt_sk_...)."""
    __tablename__ = "api_keys"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key_hash: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    key_prefix: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="api_keys")
    runs: Mapped[List["Run"]] = relationship("Run", back_populates="api_key")


class Dataset(Base):
    """Datasets (ingredients) - metadata stored in PostgreSQL, content in App Storage."""
    __tablename__ = "datasets"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_bucket: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="pantry",
    )
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[DatasetStatus] = mapped_column(
        Enum(DatasetStatus, native_enum=False),
        nullable=False,
        default=DatasetStatus.uploaded,
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="datasets")
    kytchen_links: Mapped[List["KytchenDataset"]] = relationship(
        "KytchenDataset",
        back_populates="dataset",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("datasets_workspace_id_idx", "workspace_id"),
        Index("datasets_content_hash_idx", "content_hash"),
    )


class Run(Base):
    """Runs (tickets) - execution records for queries."""
    __tablename__ = "runs"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    api_key_id: Mapped[UUID | None] = mapped_column(
        GUID(),
        ForeignKey("api_keys.id", ondelete="SET NULL"),
        nullable=True,
    )
    kytchen_id: Mapped[UUID | None] = mapped_column(
        GUID(),
        ForeignKey("kytchens.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_ids: Mapped[list] = mapped_column(
        UUIDArray(),
        nullable=False,
        default=list,
    )
    budget: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, native_enum=False),
        nullable=False,
        default=RunStatus.queued,
    )
    tool_session_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    e2b_sandbox_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    success: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="runs")
    api_key: Mapped["APIKey | None"] = relationship("APIKey", back_populates="runs")
    kytchen: Mapped["Kytchen | None"] = relationship(
        "Kytchen",
        back_populates="runs",
        foreign_keys=[kytchen_id],
    )
    evidence: Mapped[List["Evidence"]] = relationship(
        "Evidence",
        back_populates="run",
        cascade="all, delete-orphan",
    )

    # Indexes
    __table_args__ = (
        Index("runs_workspace_id_idx", "workspace_id"),
        Index("runs_kytchen_id_idx", "kytchen_id"),
        Index("runs_created_at_idx", "created_at"),
    )


class Evidence(Base):
    """Evidence (sauce) - audit trail of tool executions."""
    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    params: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    snippet: Mapped[str] = mapped_column(Text, nullable=False)
    line_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    e2b_execution_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="evidence")
    run: Mapped["Run"] = relationship("Run", back_populates="evidence")

    # Indexes
    __table_args__ = (
        Index("evidence_run_id_idx", "run_id"),
        Index("evidence_workspace_id_idx", "workspace_id"),
    )


class Usage(Base):
    """Usage tracking for workspace limits (storage, requests, egress)."""
    __tablename__ = "usage"

    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )
    month_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0),
    )
    storage_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    requests_this_month: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    egress_bytes_this_month: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="usage")


class AuditLog(Base):
    """Audit logs (immutable append-only) for security and compliance."""
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        GUID(),
        primary_key=True,
        default=uuid4,
        server_default=func.gen_random_uuid(),
    )
    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Event classification
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    event_category: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(Text, nullable=False, default="info")

    # Actor (who)
    actor_type: Mapped[str] = mapped_column(Text, nullable=False)
    actor_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_ip: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Target (what)
    resource_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_id: Mapped[UUID | None] = mapped_column(GUID(), nullable=True)

    # Details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)

    # Immutability
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    previous_hash: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Indexes
    __table_args__ = (
        Index("audit_logs_workspace_id_idx", "workspace_id"),
        Index("audit_logs_created_at_idx", "created_at"),
        Index("audit_logs_event_type_idx", "event_type"),
    )


class Billing(Base):
    """Billing information (Stripe integration)."""
    __tablename__ = "billing"

    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    stripe_price_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    subscription_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_period_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancel_at_period_end: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class SandboxSession(Base):
    """Sandbox session tracking (E2B integration)."""
    __tablename__ = "sandbox_sessions"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    run_id: Mapped[UUID | None] = mapped_column(
        GUID(),
        ForeignKey("runs.id", ondelete="SET NULL"),
        nullable=True,
    )
    e2b_sandbox_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    context_id: Mapped[str] = mapped_column(Text, nullable=False, default="default")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    session_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)


# -----------------------------------------------------------------------------
# Kitchen Models (SHA-107: Menu API)
# -----------------------------------------------------------------------------


class KytchenVisibility(str, enum.Enum):
    """Kytchen visibility levels."""
    public = "public"
    private = "private"
    unlisted = "unlisted"


class Kytchen(Base):
    """Kytchen = Running environment (like a Heroku app).

    A Kitchen contains:
    - Pantry (indexed datasets)
    - Menu (available tools, OpenAI-compatible)
    - Tickets (active queries/runs)
    - Receipts (logs)
    - Sauce (evidence trail)
    """
    __tablename__ = "kytchens"

    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    visibility: Mapped[KytchenVisibility] = mapped_column(
        Enum(KytchenVisibility, native_enum=False),
        nullable=False,
        default=KytchenVisibility.private,
    )
    forked_from_id: Mapped[UUID | None] = mapped_column(
        GUID(),
        ForeignKey("kytchens.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Budget defaults for this kitchen
    budget_defaults: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    # Custom tools beyond the default ones
    custom_tools: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="kytchens")
    forked_from: Mapped["Kytchen | None"] = relationship(
        "Kytchen",
        remote_side="Kytchen.id",
        foreign_keys=[forked_from_id],
    )
    pantry_items: Mapped[List["KytchenDataset"]] = relationship(
        "KytchenDataset",
        back_populates="kytchen",
        cascade="all, delete-orphan",
    )
    runs: Mapped[List["Run"]] = relationship(
        "Run",
        back_populates="kytchen",
        foreign_keys="Run.kytchen_id",
    )

    # Indexes
    __table_args__ = (
        Index("kytchens_workspace_id_idx", "workspace_id"),
        Index("kytchens_workspace_slug_idx", "workspace_id", "slug", unique=True),
    )


class KytchenDataset(Base):
    """Junction table: Kytchen <-> Dataset (Pantry items).

    Allows a dataset to be in multiple kitchens, and tracks
    kitchen-specific metadata like indexing status.
    """
    __tablename__ = "kytchen_datasets"

    kytchen_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("kytchens.id", ondelete="CASCADE"),
        primary_key=True,
    )
    dataset_id: Mapped[UUID] = mapped_column(
        GUID(),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        primary_key=True,
    )
    # Kitchen-specific indexing status
    indexed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    kytchen: Mapped["Kytchen"] = relationship("Kytchen", back_populates="pantry_items")
    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="kytchen_links")

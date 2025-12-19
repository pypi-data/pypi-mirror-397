"""Tier-based resource limits for Kytchen workspaces.

Implements the "Costco model" tier limits:
- Starter (free): 1GB storage, 5 req/min, 0 E2B Lines
- Chef ($35/mo): 10GB storage, 100 req/min, 1 E2B Line
- Sous Chef ($99/mo): 50GB storage, 200 req/min, 3 E2B Lines

"Pay membership, use the kitchen. No games, no tricks."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, Literal

try:
    from fastapi import HTTPException
    from sqlalchemy import func, select
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    HTTPException = Exception  # type: ignore[assignment,misc]
    func = None  # type: ignore[assignment]
    select = None  # type: ignore[assignment]
    SQLALCHEMY_AVAILABLE = False

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

# Conditional model imports
if SQLALCHEMY_AVAILABLE:
    from .models import SandboxSession, Usage, Workspace, WorkspacePlan
else:
    # Stubs for when SQLAlchemy is not available
    SandboxSession = Any  # type: ignore[assignment,misc]
    Usage = Any  # type: ignore[assignment,misc]
    Workspace = Any  # type: ignore[assignment,misc]

    class WorkspacePlan:  # type: ignore[no-redef]
        """Stub for WorkspacePlan enum."""
        free = "free"
        pro = "pro"
        team = "team"


PlanName = Literal["free", "pro", "team"]


BYTES_PER_MB: Final[int] = 1024 * 1024
BYTES_PER_GB: Final[int] = 1024 * 1024 * 1024


@dataclass(frozen=True, slots=True)
class PlanLimits:
    pantry_storage_bytes: int
    rate_limit_per_min: int
    tool_timeout_seconds: int
    egress_bytes_per_month: int
    sauce_retention_days: int
    e2b_lines: int  # Number of E2B sandboxes allowed


PLAN_LIMITS: Final[dict[PlanName, PlanLimits]] = {
    # Starter (Free): 1GB, 5 req/min, 15s timeout, 1GB/mo egress, 3 days retention, 0 lines
    "free": PlanLimits(
        pantry_storage_bytes=1 * BYTES_PER_GB,
        rate_limit_per_min=5,
        tool_timeout_seconds=15,
        egress_bytes_per_month=1 * BYTES_PER_GB,
        sauce_retention_days=3,
        e2b_lines=0,
    ),
    # Chef ($35/mo): 10GB, 100 req/min, 60s timeout, 50GB/mo egress, 90 days retention, 1 line
    "pro": PlanLimits(
        pantry_storage_bytes=10 * BYTES_PER_GB,
        rate_limit_per_min=100,
        tool_timeout_seconds=60,
        egress_bytes_per_month=50 * BYTES_PER_GB,
        sauce_retention_days=90,
        e2b_lines=1,
    ),
    # Sous Chef ($99/mo): 50GB, 200 req/min, 120s timeout, 200GB/mo egress, 1 year retention, 3 lines
    "team": PlanLimits(
        pantry_storage_bytes=50 * BYTES_PER_GB,
        rate_limit_per_min=200,
        tool_timeout_seconds=120,
        egress_bytes_per_month=200 * BYTES_PER_GB,
        sauce_retention_days=365,
        e2b_lines=3,
    ),
}


# Tier limit definitions (dictionary format for API responses)
TIER_LIMITS = {
    WorkspacePlan.free: {
        "storage_gb": 1,
        "rate_per_min": 5,
        "lines": 0,  # E2B sandboxes allowed
        "tier_name": "Starter",
    },
    WorkspacePlan.pro: {
        "storage_gb": 10,
        "rate_per_min": 100,
        "lines": 1,
        "tier_name": "Chef",
    },
    WorkspacePlan.team: {
        "storage_gb": 50,
        "rate_per_min": 200,
        "lines": 3,
        "tier_name": "Sous Chef",
    },
}


def get_plan_limits(plan: str) -> PlanLimits:
    """Get plan limits by plan name string.

    Args:
        plan: Plan name ("free", "pro", "team").

    Returns:
        PlanLimits dataclass with all limits for the plan.
    """
    normalized = plan.strip().lower()
    if normalized in PLAN_LIMITS:
        return PLAN_LIMITS[normalized]  # type: ignore[index]
    return PLAN_LIMITS["free"]


def get_tier_limits(plan: WorkspacePlan) -> dict:
    """Get limits for a workspace plan tier.

    Args:
        plan: The workspace plan enum value.

    Returns:
        Dictionary with storage_gb, rate_per_min, lines, and tier_name.
    """
    return TIER_LIMITS.get(plan, TIER_LIMITS[WorkspacePlan.free])


async def check_lines_limit(
    workspace_id: str,
    db: "AsyncSession",
) -> tuple[bool, int, int]:
    """Check if workspace can create more E2B Lines.

    Args:
        workspace_id: The workspace UUID as a string.
        db: Async database session.

    Returns:
        Tuple of (can_create, current_count, max_allowed).
    """
    # Get workspace and its plan
    workspace = await db.get(Workspace, workspace_id)
    if not workspace:
        return False, 0, 0

    limits = get_tier_limits(workspace.plan)
    max_lines = limits["lines"]

    # Count current active lines (SandboxSession with status='active')
    result = await db.execute(
        select(func.count(SandboxSession.id))
        .where(SandboxSession.workspace_id == workspace_id)
        .where(SandboxSession.status == "active")
    )
    current_count = result.scalar() or 0

    return current_count < max_lines, current_count, max_lines


async def check_storage_limit(
    workspace_id: str,
    db: "AsyncSession",
    additional_bytes: int = 0,
) -> tuple[bool, int, int]:
    """Check if workspace is within storage limits.

    Args:
        workspace_id: The workspace UUID as a string.
        db: Async database session.
        additional_bytes: Additional bytes to be added (for upload checks).

    Returns:
        Tuple of (within_limit, current_bytes, max_bytes).
    """
    # Get workspace and its plan
    workspace = await db.get(Workspace, workspace_id)
    if not workspace:
        return False, 0, 0

    limits = get_tier_limits(workspace.plan)
    max_bytes = limits["storage_gb"] * BYTES_PER_GB

    # Get current storage usage
    result = await db.execute(
        select(Usage.storage_bytes).where(Usage.workspace_id == workspace_id)
    )
    current_bytes = result.scalar() or 0

    return (current_bytes + additional_bytes) <= max_bytes, current_bytes, max_bytes


class TierLimitError(HTTPException):
    """Raised when a tier limit is exceeded (payment required to upgrade)."""

    def __init__(self, limit_type: str, current: int, max_allowed: int, tier_name: str):
        """Create a tier limit error.

        Args:
            limit_type: Type of limit exceeded (e.g., "E2B Lines", "Storage").
            current: Current usage count.
            max_allowed: Maximum allowed by the tier.
            tier_name: Display name of the tier (e.g., "Starter", "Chef").
        """
        detail = (
            f"{limit_type} limit reached. "
            f"Current: {current}, Max: {max_allowed} for {tier_name} tier. "
            f"Upgrade your plan to increase limits."
        )
        # 402 Payment Required - user needs to upgrade their tier
        super().__init__(status_code=402, detail=detail)


class StorageLimitError(TierLimitError):
    """Raised when storage limit is exceeded."""

    def __init__(self, current_gb: float, max_gb: int, tier_name: str):
        """Create a storage limit error.

        Args:
            current_gb: Current storage usage in GB.
            max_gb: Maximum storage allowed in GB.
            tier_name: Display name of the tier.
        """
        detail = (
            f"Storage limit reached. "
            f"Current: {current_gb:.2f} GB, Max: {max_gb} GB for {tier_name} tier. "
            f"Upgrade your plan to increase limits."
        )
        HTTPException.__init__(self, status_code=403, detail=detail)


class RateLimitError(HTTPException):
    """Raised when rate limit is exceeded."""

    def __init__(self, tier_name: str, rate_limit: int):
        """Create a rate limit error.

        Args:
            tier_name: Display name of the tier.
            rate_limit: Requests per minute allowed.
        """
        detail = (
            f"Rate limit exceeded. "
            f"Maximum {rate_limit} requests/minute for {tier_name} tier. "
            f"Upgrade your plan to increase limits."
        )
        super().__init__(status_code=429, detail=detail)


# Export all public symbols
__all__ = [
    "BYTES_PER_GB",
    "BYTES_PER_MB",
    "PLAN_LIMITS",
    "TIER_LIMITS",
    "PlanLimits",
    "PlanName",
    "RateLimitError",
    "StorageLimitError",
    "TierLimitError",
    "check_lines_limit",
    "check_storage_limit",
    "get_plan_limits",
    "get_tier_limits",
]


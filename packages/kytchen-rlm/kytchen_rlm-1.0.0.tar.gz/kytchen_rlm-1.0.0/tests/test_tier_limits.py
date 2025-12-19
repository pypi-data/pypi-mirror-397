"""Tests for tier-based resource limits (SHA-139).

Tests the enforcement of:
- E2B Lines limits (402 Payment Required)
- Storage limits (403 Forbidden)
- Rate limits (429 Too Many Requests)
"""

from __future__ import annotations

import os

import pytest

# Set dev mode before importing app
os.environ["KYTCHEN_DEV_MODE"] = "1"

from kytchen.api.limits import (
    PLAN_LIMITS,
    TierLimitError,
    StorageLimitError,
    RateLimitError,
    get_plan_limits,
)


# Check for optional dependencies
try:
    import httpx
    import fastapi
    import sqlalchemy
    INTEGRATION_DEPS = True
except ImportError:
    INTEGRATION_DEPS = False

try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False


# -----------------------------------------------------------------------------
# Unit Tests for Limit Classes
# -----------------------------------------------------------------------------


def test_tier_limit_error_returns_402() -> None:
    """TierLimitError should return HTTP 402 (Payment Required)."""
    error = TierLimitError("E2B Lines", 1, 1, "Chef")
    assert error.status_code == 402
    assert "E2B Lines limit reached" in error.detail
    assert "Chef tier" in error.detail
    assert "Upgrade your plan" in error.detail


def test_storage_limit_error_returns_403() -> None:
    """StorageLimitError should return HTTP 403 (Forbidden)."""
    error = StorageLimitError(1.5, 1, "Starter")
    assert error.status_code == 403
    assert "Storage limit reached" in error.detail
    assert "Starter tier" in error.detail


def test_rate_limit_error_returns_429() -> None:
    """RateLimitError should return HTTP 429 (Too Many Requests)."""
    error = RateLimitError("Starter", 5)
    assert error.status_code == 429
    assert "Rate limit exceeded" in error.detail
    assert "5 requests/minute" in error.detail


# -----------------------------------------------------------------------------
# Unit Tests for Plan Limits
# -----------------------------------------------------------------------------


def test_plan_limits_free_tier() -> None:
    """Free tier should have restricted limits."""
    limits = get_plan_limits("free")
    assert limits.e2b_lines == 0  # No E2B access
    assert limits.rate_limit_per_min == 5
    assert limits.pantry_storage_bytes == 1 * 1024 * 1024 * 1024  # 1GB


def test_plan_limits_pro_tier() -> None:
    """Pro tier should have moderate limits."""
    limits = get_plan_limits("pro")
    assert limits.e2b_lines == 1
    assert limits.rate_limit_per_min == 100
    assert limits.pantry_storage_bytes == 10 * 1024 * 1024 * 1024  # 10GB


def test_plan_limits_team_tier() -> None:
    """Team tier should have generous limits."""
    limits = get_plan_limits("team")
    assert limits.e2b_lines == 3
    assert limits.rate_limit_per_min == 200
    assert limits.pantry_storage_bytes == 50 * 1024 * 1024 * 1024  # 50GB


def test_plan_limits_unknown_falls_back_to_free() -> None:
    """Unknown plan should fall back to free tier."""
    limits = get_plan_limits("unknown")
    assert limits.e2b_lines == 0
    assert limits.rate_limit_per_min == 5


@pytest.mark.skipif(not INTEGRATION_DEPS, reason="SQLAlchemy not installed")
def test_get_tier_limits_returns_dict() -> None:
    """get_tier_limits should return dictionary format."""
    from kytchen.api.limits import get_tier_limits
    from kytchen.api.models import WorkspacePlan

    limits = get_tier_limits(WorkspacePlan.pro)
    assert limits["lines"] == 1
    assert limits["rate_per_min"] == 100
    assert limits["tier_name"] == "Chef"


# -----------------------------------------------------------------------------
# Error Response Format Tests
# -----------------------------------------------------------------------------


def test_tier_limit_error_message_format() -> None:
    """TierLimitError should have properly formatted message."""
    error = TierLimitError("E2B Lines", 1, 1, "Chef")
    # Check message contains all required info
    assert "E2B Lines limit reached" in error.detail
    assert "Current: 1" in error.detail
    assert "Max: 1" in error.detail
    assert "Chef tier" in error.detail
    assert "Upgrade your plan" in error.detail


def test_storage_limit_error_message_format() -> None:
    """StorageLimitError should have properly formatted message."""
    error = StorageLimitError(1.5, 1, "Starter")
    assert "Storage limit reached" in error.detail
    assert "1.50 GB" in error.detail
    assert "Max: 1 GB" in error.detail
    assert "Starter tier" in error.detail


def test_rate_limit_error_message_format() -> None:
    """RateLimitError should have properly formatted message."""
    error = RateLimitError("Chef", 100)
    assert "Rate limit exceeded" in error.detail
    assert "100 requests/minute" in error.detail
    assert "Chef tier" in error.detail


# -----------------------------------------------------------------------------
# Integration Tests - Rate Limiting (429)
# These require aiosqlite for in-memory SQLite
# -----------------------------------------------------------------------------


@pytest.fixture
def app():
    """Create a fresh app instance for each test."""
    pytest.importorskip("fastapi")
    pytest.importorskip("httpx")
    pytest.importorskip("sqlalchemy")
    pytest.importorskip("aiosqlite")

    from kytchen.api.app import create_app
    return create_app()


@pytest.fixture
async def client(app):
    """Create an async HTTP client with proper startup/shutdown."""
    import httpx
    import kytchen.api.db as db_module

    # Reset global state for fresh in-memory database per test
    db_module._engine = None
    db_module._AsyncSessionLocal = None

    # Initialize database tables for tests
    await db_module.init_db()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    # Cleanup - dispose engine to allow fresh DB for next test
    engine = db_module._get_engine()
    if engine:
        await engine.dispose()
    db_module._engine = None
    db_module._AsyncSessionLocal = None


AUTH_HEADERS = {"Authorization": "Bearer kyt_sk_test_key"}


@pytest.mark.asyncio
@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
async def test_rate_limit_returns_429(client) -> None:
    """Rate limiting middleware should return 429 after exceeding limit."""
    # Free plan allows 5 requests/minute
    for _ in range(5):
        r = await client.get("/healthz", headers=AUTH_HEADERS)
        assert r.status_code == 200

    # 6th request should be rate limited
    r = await client.get("/healthz", headers=AUTH_HEADERS)
    assert r.status_code == 429
    assert "Rate limit exceeded" in r.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
async def test_lines_limit_free_tier_returns_402(client) -> None:
    """Free tier (0 lines) should return 402 when creating a line."""
    # Create a kitchen first
    kitchen_payload = {"name": "Lines Test Kitchen"}
    r = await client.post("/v1/kytchens", json=kitchen_payload, headers=AUTH_HEADERS)
    assert r.status_code == 201
    kitchen_id = r.json()["id"]

    # Try to create a line (free tier has 0 lines)
    r = await client.post(
        f"/v1/kytchens/{kitchen_id}/lines",
        json={},
        headers=AUTH_HEADERS,
    )
    # Should return 402 because free tier has 0 lines allowed
    assert r.status_code == 402
    assert "E2B Lines limit reached" in r.json()["detail"]
    assert "Max: 0" in r.json()["detail"]


# -----------------------------------------------------------------------------
# Database Function Tests
# These require aiosqlite for in-memory SQLite
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
async def test_check_lines_limit_free_tier() -> None:
    """check_lines_limit should return False for free tier (0 lines allowed)."""
    from kytchen.api.limits import check_lines_limit
    import kytchen.api.db as db_module
    from kytchen.api.models import Workspace, WorkspacePlan
    from uuid import uuid4

    # Reset DB
    db_module._engine = None
    db_module._AsyncSessionLocal = None
    await db_module.init_db()

    async with db_module.AsyncSessionLocal() as session:
        # Create a free tier workspace
        ws_id = uuid4()
        workspace = Workspace(
            id=ws_id,
            name="Test Workspace",
            slug="test-workspace",
            plan=WorkspacePlan.free,
        )
        session.add(workspace)
        await session.commit()

        # Check lines limit
        can_create, current, max_allowed = await check_lines_limit(str(ws_id), session)

        # Free tier should not allow any lines
        assert can_create is False
        assert current == 0
        assert max_allowed == 0

    # Cleanup
    engine = db_module._get_engine()
    if engine:
        await engine.dispose()
    db_module._engine = None
    db_module._AsyncSessionLocal = None


@pytest.mark.asyncio
@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
async def test_check_lines_limit_pro_tier() -> None:
    """check_lines_limit should allow 1 line for pro tier."""
    from kytchen.api.limits import check_lines_limit
    import kytchen.api.db as db_module
    from kytchen.api.models import Workspace, WorkspacePlan
    from uuid import uuid4

    # Reset DB
    db_module._engine = None
    db_module._AsyncSessionLocal = None
    await db_module.init_db()

    async with db_module.AsyncSessionLocal() as session:
        # Create a pro tier workspace
        ws_id = uuid4()
        workspace = Workspace(
            id=ws_id,
            name="Pro Workspace",
            slug="pro-workspace",
            plan=WorkspacePlan.pro,
        )
        session.add(workspace)
        await session.commit()

        # Check lines limit
        can_create, current, max_allowed = await check_lines_limit(str(ws_id), session)

        # Pro tier should allow 1 line
        assert can_create is True
        assert current == 0
        assert max_allowed == 1

    # Cleanup
    engine = db_module._get_engine()
    if engine:
        await engine.dispose()
    db_module._engine = None
    db_module._AsyncSessionLocal = None


@pytest.mark.asyncio
@pytest.mark.skipif(not AIOSQLITE_AVAILABLE, reason="aiosqlite not installed")
async def test_check_storage_limit_within_limit() -> None:
    """check_storage_limit should return True when within limit."""
    from kytchen.api.limits import check_storage_limit
    import kytchen.api.db as db_module
    from kytchen.api.models import Workspace, WorkspacePlan
    from uuid import uuid4

    # Reset DB
    db_module._engine = None
    db_module._AsyncSessionLocal = None
    await db_module.init_db()

    async with db_module.AsyncSessionLocal() as session:
        # Create a workspace
        ws_id = uuid4()
        workspace = Workspace(
            id=ws_id,
            name="Storage Test",
            slug="storage-test",
            plan=WorkspacePlan.free,
        )
        session.add(workspace)
        await session.commit()

        # Check storage limit with no additional bytes
        within_limit, current, max_bytes = await check_storage_limit(str(ws_id), session)

        # Should be within limit (0 bytes used of 1GB)
        assert within_limit is True
        assert current == 0
        assert max_bytes == 1 * 1024 * 1024 * 1024

    # Cleanup
    engine = db_module._get_engine()
    if engine:
        await engine.dispose()
    db_module._engine = None
    db_module._AsyncSessionLocal = None


# -----------------------------------------------------------------------------
# HTTP Status Code Verification Tests
# These verify the expected status codes in limits.py
# -----------------------------------------------------------------------------


def test_http_status_codes_are_correct() -> None:
    """Verify the HTTP status codes match specifications.

    - 402 Payment Required: For tier limits (need to upgrade plan)
    - 403 Forbidden: For storage limits (currently forbidden)
    - 429 Too Many Requests: For rate limits
    """
    # Tier limits: 402 Payment Required
    tier_error = TierLimitError("Lines", 0, 0, "Test")
    assert tier_error.status_code == 402, "TierLimitError should use 402 (Payment Required)"

    # Storage limits: 403 Forbidden
    storage_error = StorageLimitError(1.0, 1, "Test")
    assert storage_error.status_code == 403, "StorageLimitError should use 403 (Forbidden)"

    # Rate limits: 429 Too Many Requests
    rate_error = RateLimitError("Test", 5)
    assert rate_error.status_code == 429, "RateLimitError should use 429 (Too Many Requests)"


def test_all_tiers_have_e2b_lines_defined() -> None:
    """All tiers should have e2b_lines defined."""
    for tier_name in ["free", "pro", "team"]:
        limits = get_plan_limits(tier_name)
        assert hasattr(limits, "e2b_lines"), f"{tier_name} tier missing e2b_lines"
        assert isinstance(limits.e2b_lines, int), f"{tier_name} tier e2b_lines should be int"


def test_tier_limits_are_monotonically_increasing() -> None:
    """Higher tiers should have equal or greater limits than lower tiers."""
    free = get_plan_limits("free")
    pro = get_plan_limits("pro")
    team = get_plan_limits("team")

    # E2B lines should increase: free < pro < team
    assert free.e2b_lines <= pro.e2b_lines, "Pro should have >= lines than free"
    assert pro.e2b_lines <= team.e2b_lines, "Team should have >= lines than pro"

    # Rate limits should increase
    assert free.rate_limit_per_min <= pro.rate_limit_per_min
    assert pro.rate_limit_per_min <= team.rate_limit_per_min

    # Storage should increase
    assert free.pantry_storage_bytes <= pro.pantry_storage_bytes
    assert pro.pantry_storage_bytes <= team.pantry_storage_bytes

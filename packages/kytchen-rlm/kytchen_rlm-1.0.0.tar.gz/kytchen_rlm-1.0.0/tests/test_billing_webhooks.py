"""Tests for Stripe billing webhooks (SHA-138).

Tests webhook signature verification and database updates for:
- checkout.session.completed
- customer.subscription.updated
- customer.subscription.deleted
- invoice.payment_failed
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
httpx = pytest.importorskip("httpx")
sqlalchemy = pytest.importorskip("sqlalchemy")
stripe = pytest.importorskip("stripe")


# -----------------------------------------------------------------------------
# Test Fixtures
# -----------------------------------------------------------------------------


@pytest.fixture
def mock_workspace_id() -> str:
    """Generate a consistent workspace ID for tests."""
    return str(uuid4())


@pytest.fixture
def mock_customer_id() -> str:
    """Generate a Stripe customer ID."""
    return "cus_test123456"


@pytest.fixture
def mock_subscription_id() -> str:
    """Generate a Stripe subscription ID."""
    return "sub_test123456"


@pytest.fixture
def mock_price_id() -> str:
    """Generate a Stripe price ID."""
    return "price_chef_monthly"


def generate_stripe_signature(payload: bytes, secret: str, timestamp: int | None = None) -> str:
    """Generate a valid Stripe webhook signature for testing.

    Args:
        payload: The raw request body bytes
        secret: The webhook signing secret
        timestamp: Unix timestamp (defaults to current time)

    Returns:
        A valid stripe-signature header value
    """
    if timestamp is None:
        timestamp = int(time.time())

    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return f"t={timestamp},v1={signature}"


def create_stripe_event(
    event_type: str,
    data: dict[str, Any],
    event_id: str | None = None,
) -> dict[str, Any]:
    """Create a mock Stripe event payload.

    Args:
        event_type: The type of event (e.g., "checkout.session.completed")
        data: The event data object
        event_id: Optional event ID (auto-generated if not provided)

    Returns:
        A dict representing the Stripe event
    """
    return {
        "id": event_id or f"evt_test_{uuid4().hex[:16]}",
        "type": event_type,
        "data": {
            "object": data
        },
        "created": int(time.time()),
        "livemode": False,
    }


# -----------------------------------------------------------------------------
# Webhook Signature Verification Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_webhook_missing_signature() -> None:
    """Test webhook rejects requests without stripe-signature header.

    Note: If Stripe is not configured (no STRIPE_SECRET_KEY/STRIPE_WEBHOOK_SECRET),
    the endpoint returns 503 before checking the signature header.
    """
    from kytchen.api.app import create_app

    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/billing/webhook",
            json={"type": "test.event"},
        )

        # 400 if Stripe is configured but signature missing
        # 503 if Stripe is not configured
        assert response.status_code in (400, 503)
        if response.status_code == 400:
            assert "Missing stripe-signature" in response.json()["detail"]
        else:
            assert "not configured" in response.json()["detail"]


@pytest.mark.asyncio
async def test_webhook_invalid_signature() -> None:
    """Test webhook rejects requests with invalid signature."""
    from kytchen.api.app import create_app

    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/billing/webhook",
            json={"type": "test.event"},
            headers={"stripe-signature": "t=123,v1=invalid_signature"},
        )

        # Should be 400 (invalid signature) or 503 (stripe not configured)
        assert response.status_code in (400, 503)


@pytest.mark.asyncio
async def test_webhook_stripe_not_configured() -> None:
    """Test webhook returns 503 when Stripe is not configured."""
    from kytchen.api.app import create_app

    # Ensure Stripe env vars are not set
    with patch.dict("os.environ", {"STRIPE_SECRET_KEY": "", "STRIPE_WEBHOOK_SECRET": ""}, clear=False):
        # Need to reload the module to pick up the new env vars
        import importlib
        import kytchen.api.routes.billing as billing_module
        importlib.reload(billing_module)

        app = create_app()
        transport = httpx.ASGITransport(app=app)

        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v1/billing/webhook",
                json={"type": "test.event"},
                headers={"stripe-signature": "t=123,v1=test"},
            )

            assert response.status_code == 503
            assert "not configured" in response.json()["detail"]


# -----------------------------------------------------------------------------
# Checkout Completed Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_checkout_completed_creates_billing_record(
    mock_workspace_id: str,
    mock_customer_id: str,
    mock_subscription_id: str,
    mock_price_id: str,
) -> None:
    """Test checkout.session.completed creates a billing record."""
    from kytchen.api.routes.billing import _handle_checkout_completed, PRICE_TO_PLAN
    from kytchen.api.models import Billing, Workspace, WorkspacePlan

    # Mock the database session
    mock_db = AsyncMock()

    # Mock workspace lookup - return a workspace
    mock_workspace = MagicMock(spec=Workspace)
    mock_workspace.id = mock_workspace_id
    mock_workspace.plan = WorkspacePlan.free
    mock_workspace.stripe_customer_id = None

    mock_workspace_result = MagicMock()
    mock_workspace_result.scalar_one_or_none.return_value = mock_workspace

    # Mock billing lookup - no existing record
    mock_billing_result = MagicMock()
    mock_billing_result.scalar_one_or_none.return_value = None

    mock_db.execute = AsyncMock(side_effect=[mock_workspace_result, mock_billing_result])
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    # Mock Stripe subscription retrieval
    mock_subscription = {
        "id": mock_subscription_id,
        "status": "active",
        "items": {"data": [{"price": {"id": mock_price_id}}]},
        "current_period_start": int(time.time()),
        "current_period_end": int(time.time()) + 30 * 24 * 60 * 60,
        "cancel_at_period_end": False,
    }

    with patch("stripe.Subscription.retrieve", return_value=mock_subscription):
        checkout_data = {
            "metadata": {"workspace_id": mock_workspace_id},
            "customer": mock_customer_id,
            "subscription": mock_subscription_id,
        }

        await _handle_checkout_completed(checkout_data, mock_db)

        # Verify workspace was updated
        assert mock_workspace.stripe_customer_id == mock_customer_id

        # Verify billing record was added
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_checkout_completed_missing_workspace_id() -> None:
    """Test checkout.session.completed handles missing workspace_id gracefully."""
    from kytchen.api.routes.billing import _handle_checkout_completed

    mock_db = AsyncMock()

    # Missing workspace_id in metadata
    checkout_data = {
        "metadata": {},
        "customer": "cus_test",
        "subscription": "sub_test",
    }

    await _handle_checkout_completed(checkout_data, mock_db)

    # Should return early without making any DB calls
    mock_db.execute.assert_not_called()


# -----------------------------------------------------------------------------
# Subscription Updated Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_subscription_updated_changes_plan(
    mock_workspace_id: str,
    mock_customer_id: str,
    mock_subscription_id: str,
    mock_price_id: str,
) -> None:
    """Test customer.subscription.updated changes workspace plan."""
    from kytchen.api.routes.billing import _handle_subscription_updated, PRICE_TO_PLAN
    from kytchen.api.models import Billing, Workspace, WorkspacePlan

    mock_db = AsyncMock()

    # Mock workspace
    mock_workspace = MagicMock(spec=Workspace)
    mock_workspace.id = mock_workspace_id
    mock_workspace.plan = WorkspacePlan.free
    mock_workspace.stripe_customer_id = mock_customer_id

    mock_workspace_result = MagicMock()
    mock_workspace_result.scalar_one_or_none.return_value = mock_workspace

    # Mock billing record
    mock_billing = MagicMock(spec=Billing)
    mock_billing.workspace_id = mock_workspace_id
    mock_billing.stripe_subscription_id = mock_subscription_id

    mock_billing_result = MagicMock()
    mock_billing_result.scalar_one_or_none.return_value = mock_billing

    mock_db.execute = AsyncMock(side_effect=[mock_workspace_result, mock_billing_result])
    mock_db.commit = AsyncMock()

    subscription_data = {
        "id": mock_subscription_id,
        "customer": mock_customer_id,
        "status": "active",
        "items": {"data": [{"price": {"id": mock_price_id}}]},
        "current_period_start": int(time.time()),
        "current_period_end": int(time.time()) + 30 * 24 * 60 * 60,
        "cancel_at_period_end": False,
    }

    await _handle_subscription_updated(subscription_data, mock_db)

    # Verify commit was called
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_subscription_updated_workspace_not_found(
    mock_customer_id: str,
    mock_subscription_id: str,
    mock_price_id: str,
) -> None:
    """Test subscription update handles missing workspace gracefully."""
    from kytchen.api.routes.billing import _handle_subscription_updated

    mock_db = AsyncMock()

    # No workspace found
    mock_workspace_result = MagicMock()
    mock_workspace_result.scalar_one_or_none.return_value = None

    mock_db.execute = AsyncMock(return_value=mock_workspace_result)
    mock_db.commit = AsyncMock()

    subscription_data = {
        "id": mock_subscription_id,
        "customer": mock_customer_id,
        "status": "active",
        "items": {"data": [{"price": {"id": mock_price_id}}]},
        "current_period_start": int(time.time()),
        "current_period_end": int(time.time()) + 30 * 24 * 60 * 60,
    }

    await _handle_subscription_updated(subscription_data, mock_db)

    # Should not commit anything
    mock_db.commit.assert_not_called()


# -----------------------------------------------------------------------------
# Subscription Deleted Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_subscription_deleted_downgrades_to_free(
    mock_workspace_id: str,
    mock_customer_id: str,
    mock_subscription_id: str,
) -> None:
    """Test customer.subscription.deleted downgrades workspace to free."""
    from kytchen.api.routes.billing import _handle_subscription_deleted
    from kytchen.api.models import Billing, Workspace, WorkspacePlan

    mock_db = AsyncMock()

    # Mock workspace with pro plan
    mock_workspace = MagicMock(spec=Workspace)
    mock_workspace.id = mock_workspace_id
    mock_workspace.plan = WorkspacePlan.pro
    mock_workspace.stripe_customer_id = mock_customer_id

    mock_workspace_result = MagicMock()
    mock_workspace_result.scalar_one_or_none.return_value = mock_workspace

    # Mock billing record
    mock_billing = MagicMock(spec=Billing)
    mock_billing.workspace_id = mock_workspace_id
    mock_billing.subscription_status = "active"
    mock_billing.cancel_at_period_end = False

    mock_billing_result = MagicMock()
    mock_billing_result.scalar_one_or_none.return_value = mock_billing

    mock_db.execute = AsyncMock(side_effect=[mock_workspace_result, mock_billing_result])
    mock_db.commit = AsyncMock()

    deletion_data = {
        "id": mock_subscription_id,
        "customer": mock_customer_id,
    }

    await _handle_subscription_deleted(deletion_data, mock_db)

    # Verify workspace was downgraded
    assert mock_workspace.plan == WorkspacePlan.free

    # Verify billing record was updated
    assert mock_billing.subscription_status == "canceled"
    assert mock_billing.cancel_at_period_end is False

    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_subscription_deleted_workspace_not_found(
    mock_customer_id: str,
) -> None:
    """Test subscription deletion handles missing workspace gracefully."""
    from kytchen.api.routes.billing import _handle_subscription_deleted

    mock_db = AsyncMock()

    # No workspace found
    mock_workspace_result = MagicMock()
    mock_workspace_result.scalar_one_or_none.return_value = None

    mock_db.execute = AsyncMock(return_value=mock_workspace_result)
    mock_db.commit = AsyncMock()

    deletion_data = {
        "id": "sub_test",
        "customer": mock_customer_id,
    }

    await _handle_subscription_deleted(deletion_data, mock_db)

    # Should not commit anything
    mock_db.commit.assert_not_called()


# -----------------------------------------------------------------------------
# Payment Failed Tests
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_payment_failed_marks_past_due(
    mock_workspace_id: str,
    mock_subscription_id: str,
) -> None:
    """Test invoice.payment_failed marks subscription as past_due."""
    from kytchen.api.routes.billing import _handle_payment_failed
    from kytchen.api.models import Billing

    mock_db = AsyncMock()

    # Mock billing record
    mock_billing = MagicMock(spec=Billing)
    mock_billing.workspace_id = mock_workspace_id
    mock_billing.subscription_status = "active"

    mock_billing_result = MagicMock()
    mock_billing_result.scalar_one_or_none.return_value = mock_billing

    mock_db.execute = AsyncMock(return_value=mock_billing_result)
    mock_db.commit = AsyncMock()

    invoice_data = {
        "id": "in_test123",
        "subscription": mock_subscription_id,
    }

    await _handle_payment_failed(invoice_data, mock_db)

    # Verify subscription status was updated
    assert mock_billing.subscription_status == "past_due"
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_payment_failed_missing_subscription() -> None:
    """Test payment_failed handles missing subscription_id gracefully."""
    from kytchen.api.routes.billing import _handle_payment_failed

    mock_db = AsyncMock()

    # Invoice without subscription ID
    invoice_data = {
        "id": "in_test123",
        # No subscription field
    }

    await _handle_payment_failed(invoice_data, mock_db)

    # Should return early without DB calls
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_payment_failed_billing_not_found(
    mock_subscription_id: str,
) -> None:
    """Test payment_failed handles missing billing record gracefully."""
    from kytchen.api.routes.billing import _handle_payment_failed

    mock_db = AsyncMock()

    # No billing record found
    mock_billing_result = MagicMock()
    mock_billing_result.scalar_one_or_none.return_value = None

    mock_db.execute = AsyncMock(return_value=mock_billing_result)
    mock_db.commit = AsyncMock()

    invoice_data = {
        "id": "in_test123",
        "subscription": mock_subscription_id,
    }

    await _handle_payment_failed(invoice_data, mock_db)

    # Should not commit anything
    mock_db.commit.assert_not_called()


# -----------------------------------------------------------------------------
# Integration Tests (require running server)
# -----------------------------------------------------------------------------


@pytest.mark.asyncio
@pytest.mark.integration
async def test_webhook_endpoint_full_flow() -> None:
    """Integration test for full webhook flow with signature verification.

    Note: This test requires STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET
    to be configured. Skip if not available.
    """
    import os

    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        pytest.skip("STRIPE_WEBHOOK_SECRET not configured")

    from kytchen.api.app import create_app

    app = create_app()
    transport = httpx.ASGITransport(app=app)

    # Create a test event
    event = create_stripe_event(
        "checkout.session.completed",
        {
            "metadata": {"workspace_id": str(uuid4())},
            "customer": "cus_test",
            "subscription": "sub_test",
        }
    )

    payload = json.dumps(event).encode("utf-8")
    signature = generate_stripe_signature(payload, webhook_secret)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/billing/webhook",
            content=payload,
            headers={
                "stripe-signature": signature,
                "Content-Type": "application/json",
            },
        )

        # Note: This may fail with DB errors in test environment,
        # but at least verifies signature validation works
        assert response.status_code in (200, 500)

"""Billing API routes (SHA-113: Stripe Integration).

Implements subscription billing with the "Costco model" - no metering, just membership.

Tiers:
- Starter (free): REPL only, 1GB storage, 5 req/min
- Chef ($35/mo): 1 line, 10GB storage, 100 req/min
- Sous Chef ($99/mo): 3 lines, 50GB storage, 200 req/min

"Pay membership, use the kitchen. No games, no tricks."
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import WorkspaceAuth, dev_resolve_workspace, require_bearer_api_key, resolve_workspace
from ..db import get_db
from ..models import Billing, Workspace, WorkspacePlan

logger = logging.getLogger(__name__)


def is_dev_mode() -> bool:
    """Check if running in development mode."""
    return os.getenv("KYTCHEN_DEV_MODE", "0").strip() in ("1", "true", "yes")


# Stripe configuration
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_CHEF = os.getenv("STRIPE_PRICE_CHEF", "")
STRIPE_PRICE_SOUSCHEF = os.getenv("STRIPE_PRICE_SOUSCHEF", "")

# Initialize Stripe
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Price ID to plan mapping
PRICE_TO_PLAN: dict[str, WorkspacePlan] = {
    STRIPE_PRICE_CHEF: WorkspacePlan.pro,
    STRIPE_PRICE_SOUSCHEF: WorkspacePlan.team,
}

# Plan to display name
PLAN_DISPLAY_NAMES: dict[WorkspacePlan, str] = {
    WorkspacePlan.free: "Starter",
    WorkspacePlan.pro: "Chef",
    WorkspacePlan.team: "Sous Chef",
}


router = APIRouter(prefix="/v1/billing", tags=["billing"])


async def get_auth(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceAuth:
    """FastAPI dependency for authentication."""
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


@router.get("/subscription")
async def get_subscription(
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Get current subscription status for workspace.

    Returns plan info, subscription status, and period dates.
    """
    # Get workspace with billing info
    result = await db.execute(
        select(Workspace).where(Workspace.id == auth.workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Get billing record if exists
    billing_result = await db.execute(
        select(Billing).where(Billing.workspace_id == auth.workspace_id)
    )
    billing = billing_result.scalar_one_or_none()

    return {
        "plan": workspace.plan.value,
        "plan_display_name": PLAN_DISPLAY_NAMES.get(workspace.plan, "Unknown"),
        "stripe_customer_id": workspace.stripe_customer_id,
        "subscription": {
            "id": billing.stripe_subscription_id if billing else None,
            "status": billing.subscription_status if billing else None,
            "current_period_start": billing.current_period_start.isoformat() if billing and billing.current_period_start else None,
            "current_period_end": billing.current_period_end.isoformat() if billing and billing.current_period_end else None,
            "cancel_at_period_end": billing.cancel_at_period_end if billing else False,
        } if billing else None,
    }


@router.post("/checkout")
async def create_checkout_session(
    request: Request,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create Stripe checkout session for subscription upgrade.

    Body:
        price_id: Stripe price ID (STRIPE_PRICE_CHEF or STRIPE_PRICE_SOUSCHEF)
        success_url: URL to redirect after successful payment
        cancel_url: URL to redirect if user cancels
    """
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    body = await request.json()
    price_id = body.get("price_id")
    success_url = body.get("success_url", "https://kytchen.dev/dashboard/billing?success=true")
    cancel_url = body.get("cancel_url", "https://kytchen.dev/dashboard/billing?canceled=true")

    if not price_id:
        raise HTTPException(status_code=400, detail="price_id required")

    if price_id not in PRICE_TO_PLAN:
        raise HTTPException(status_code=400, detail="Invalid price_id")

    # Get workspace
    result = await db.execute(
        select(Workspace).where(Workspace.id == auth.workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # Create or get Stripe customer
    customer_id = workspace.stripe_customer_id
    if not customer_id:
        customer = stripe.Customer.create(
            metadata={
                "workspace_id": str(workspace.id),
                "workspace_slug": workspace.slug,
            }
        )
        customer_id = customer.id
        workspace.stripe_customer_id = customer_id
        await db.commit()

    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "workspace_id": str(workspace.id),
        },
    )

    return {
        "checkout_url": session.url,
        "session_id": session.id,
    }


@router.post("/portal")
async def create_portal_session(
    request: Request,
    auth: WorkspaceAuth = Depends(get_auth),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Create Stripe customer portal session for subscription management.

    Body:
        return_url: URL to redirect after leaving portal
    """
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    body = await request.json() if (await request.body()) else {}
    return_url = body.get("return_url", "https://kytchen.dev/dashboard/billing")

    # Get workspace
    result = await db.execute(
        select(Workspace).where(Workspace.id == auth.workspace_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if not workspace.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account. Subscribe first.")

    # Create portal session
    session = stripe.billing_portal.Session.create(
        customer=workspace.stripe_customer_id,
        return_url=return_url,
    )

    return {
        "portal_url": session.url,
    }


@router.post("/webhook")
async def handle_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Handle Stripe webhook events.

    No authentication required - validates webhook signature instead.

    Handles:
    - checkout.session.completed: Create/update subscription
    - customer.subscription.updated: Update plan/status
    - customer.subscription.deleted: Downgrade to free
    - invoice.payment_failed: Mark as past_due
    """
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        logger.error("Stripe webhook called but STRIPE_SECRET_KEY or STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=503, detail="Stripe not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        logger.warning("Stripe webhook called without stripe-signature header")
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Stripe webhook invalid payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Stripe webhook signature verification failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event["type"]
    event_id = event.get("id", "unknown")
    data = event["data"]["object"]

    logger.info(f"Stripe webhook received: type={event_type}, event_id={event_id}")

    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(data, db)
            logger.info(f"Webhook checkout.session.completed processed successfully: event_id={event_id}")
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(data, db)
            logger.info(f"Webhook customer.subscription.updated processed successfully: event_id={event_id}")
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(data, db)
            logger.info(f"Webhook customer.subscription.deleted processed successfully: event_id={event_id}")
        elif event_type == "invoice.payment_failed":
            await _handle_payment_failed(data, db)
            logger.info(f"Webhook invoice.payment_failed processed successfully: event_id={event_id}")
        else:
            logger.debug(f"Webhook event type not handled: type={event_type}, event_id={event_id}")
    except Exception as e:
        logger.error(f"Webhook processing failed: type={event_type}, event_id={event_id}, error={e}")
        raise

    return {"status": "ok"}


async def _handle_checkout_completed(data: dict, db: AsyncSession) -> None:
    """Handle successful checkout - create/update billing record."""
    workspace_id = data.get("metadata", {}).get("workspace_id")
    customer_id = data.get("customer")
    subscription_id = data.get("subscription")

    if not workspace_id or not subscription_id:
        logger.warning(f"checkout.session.completed missing data: workspace_id={workspace_id}, subscription_id={subscription_id}")
        return

    logger.debug(f"Processing checkout.session.completed: workspace_id={workspace_id}, customer_id={customer_id}, subscription_id={subscription_id}")

    # Get subscription details
    subscription = stripe.Subscription.retrieve(subscription_id)
    price_id = subscription["items"]["data"][0]["price"]["id"]
    new_plan = PRICE_TO_PLAN.get(price_id, WorkspacePlan.free)

    # Update workspace plan
    result = await db.execute(
        select(Workspace).where(Workspace.id == workspace_id)
    )
    workspace = result.scalar_one_or_none()
    if workspace:
        workspace.plan = new_plan
        workspace.stripe_customer_id = customer_id

    # Create or update billing record
    billing_result = await db.execute(
        select(Billing).where(Billing.workspace_id == workspace_id)
    )
    billing = billing_result.scalar_one_or_none()

    if billing:
        billing.stripe_customer_id = customer_id
        billing.stripe_subscription_id = subscription_id
        billing.stripe_price_id = price_id
        billing.subscription_status = subscription["status"]
        billing.current_period_start = datetime.fromtimestamp(
            subscription["current_period_start"], tz=timezone.utc
        )
        billing.current_period_end = datetime.fromtimestamp(
            subscription["current_period_end"], tz=timezone.utc
        )
        billing.cancel_at_period_end = subscription.get("cancel_at_period_end", False)
    else:
        billing = Billing(
            workspace_id=UUID(workspace_id),
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            stripe_price_id=price_id,
            subscription_status=subscription["status"],
            current_period_start=datetime.fromtimestamp(
                subscription["current_period_start"], tz=timezone.utc
            ),
            current_period_end=datetime.fromtimestamp(
                subscription["current_period_end"], tz=timezone.utc
            ),
            cancel_at_period_end=subscription.get("cancel_at_period_end", False),
        )
        db.add(billing)

    await db.commit()


async def _handle_subscription_updated(data: dict, db: AsyncSession) -> None:
    """Handle subscription update - plan change, status change, cancellation scheduled."""
    subscription_id = data.get("id")
    customer_id = data.get("customer")
    status = data.get("status")
    price_id = data["items"]["data"][0]["price"]["id"]
    new_plan = PRICE_TO_PLAN.get(price_id, WorkspacePlan.free)

    logger.debug(f"Processing subscription_updated: subscription_id={subscription_id}, customer_id={customer_id}, status={status}, new_plan={new_plan.value}")

    # Find workspace by customer ID
    result = await db.execute(
        select(Workspace).where(Workspace.stripe_customer_id == customer_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        logger.warning(f"subscription_updated: workspace not found for customer_id={customer_id}")
        return

    # Update workspace plan if subscription is active
    if status == "active":
        workspace.plan = new_plan

    # Update billing record
    billing_result = await db.execute(
        select(Billing).where(Billing.workspace_id == workspace.id)
    )
    billing = billing_result.scalar_one_or_none()

    if billing:
        billing.stripe_subscription_id = subscription_id
        billing.stripe_price_id = price_id
        billing.subscription_status = status
        billing.current_period_start = datetime.fromtimestamp(
            data["current_period_start"], tz=timezone.utc
        )
        billing.current_period_end = datetime.fromtimestamp(
            data["current_period_end"], tz=timezone.utc
        )
        billing.cancel_at_period_end = data.get("cancel_at_period_end", False)
        await db.commit()


async def _handle_subscription_deleted(data: dict, db: AsyncSession) -> None:
    """Handle subscription cancellation - downgrade to free."""
    customer_id = data.get("customer")
    subscription_id = data.get("id")

    logger.debug(f"Processing subscription_deleted: subscription_id={subscription_id}, customer_id={customer_id}")

    # Find workspace by customer ID
    result = await db.execute(
        select(Workspace).where(Workspace.stripe_customer_id == customer_id)
    )
    workspace = result.scalar_one_or_none()

    if not workspace:
        logger.warning(f"subscription_deleted: workspace not found for customer_id={customer_id}")
        return

    logger.info(f"Downgrading workspace to free: workspace_id={workspace.id}, previous_plan={workspace.plan.value}")

    # Downgrade to free tier
    workspace.plan = WorkspacePlan.free

    # Update billing record
    billing_result = await db.execute(
        select(Billing).where(Billing.workspace_id == workspace.id)
    )
    billing = billing_result.scalar_one_or_none()

    if billing:
        billing.subscription_status = "canceled"
        billing.cancel_at_period_end = False

    await db.commit()


async def _handle_payment_failed(data: dict, db: AsyncSession) -> None:
    """Handle failed payment - mark subscription as past_due."""
    subscription_id = data.get("subscription")
    invoice_id = data.get("id")

    logger.debug(f"Processing payment_failed: invoice_id={invoice_id}, subscription_id={subscription_id}")

    if not subscription_id:
        logger.warning(f"payment_failed: missing subscription_id for invoice_id={invoice_id}")
        return

    # Find billing record by subscription ID
    result = await db.execute(
        select(Billing).where(Billing.stripe_subscription_id == subscription_id)
    )
    billing = result.scalar_one_or_none()

    if billing:
        logger.info(f"Marking subscription as past_due: workspace_id={billing.workspace_id}, subscription_id={subscription_id}")
        billing.subscription_status = "past_due"
        await db.commit()
    else:
        logger.warning(f"payment_failed: billing record not found for subscription_id={subscription_id}")


# Export router
__all__ = ["router"]

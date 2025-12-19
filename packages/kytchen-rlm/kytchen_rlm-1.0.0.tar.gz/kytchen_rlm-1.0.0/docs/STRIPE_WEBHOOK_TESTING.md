# Stripe Webhook Testing Guide

This guide covers testing Stripe billing webhooks for Kytchen.

## Overview

The billing system handles four webhook events:

| Event | Description |
|-------|-------------|
| `checkout.session.completed` | User completes checkout - creates/updates subscription |
| `customer.subscription.updated` | Plan change, status change, cancellation scheduled |
| `customer.subscription.deleted` | Subscription canceled - downgrades to free |
| `invoice.payment_failed` | Payment failed - marks subscription as past_due |

## Local Testing with Stripe CLI

### Prerequisites

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Have the following environment variables set:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PRICE_CHEF` (price ID for Chef plan)
   - `STRIPE_PRICE_SOUSCHEF` (price ID for Sous Chef plan)

### Step 1: Login to Stripe CLI

```bash
stripe login
```

### Step 2: Start the webhook listener

In one terminal, start the local server:

```bash
# From project root
uvicorn kytchen.api.app:create_app --factory --reload --host 0.0.0.0 --port 8000
```

In another terminal, forward webhooks to your local server:

```bash
stripe listen --forward-to localhost:8000/v1/billing/webhook
```

The CLI will output a webhook signing secret (starts with `whsec_`). Use this as your `STRIPE_WEBHOOK_SECRET` for local testing.

### Step 3: Trigger test events

In a third terminal, trigger test events:

```bash
# Test checkout completion (creates subscription)
stripe trigger checkout.session.completed

# Test subscription update (plan change)
stripe trigger customer.subscription.updated

# Test subscription deletion (cancellation)
stripe trigger customer.subscription.deleted

# Test payment failure
stripe trigger invoice.payment_failed
```

### Expected Behavior

**checkout.session.completed:**
- Creates a `Billing` record for the workspace
- Updates `Workspace.plan` to the subscribed tier
- Sets `Workspace.stripe_customer_id`

**customer.subscription.updated:**
- Updates `Billing` record with new status/period
- If status is `active`, updates `Workspace.plan`

**customer.subscription.deleted:**
- Downgrades `Workspace.plan` to `free`
- Sets `Billing.subscription_status` to `canceled`

**invoice.payment_failed:**
- Sets `Billing.subscription_status` to `past_due`

## Running Automated Tests

```bash
# Run all billing webhook tests
pytest tests/test_billing_webhooks.py -v

# Run specific test
pytest tests/test_billing_webhooks.py::test_checkout_completed_creates_billing_record -v

# Run integration tests (requires Stripe credentials)
pytest tests/test_billing_webhooks.py -v -m integration
```

## Logging

Webhook handlers log at various levels:

- **INFO**: Successful webhook processing
- **WARNING**: Missing data, workspace not found
- **ERROR**: Signature verification failures, processing errors
- **DEBUG**: Detailed processing information

Enable debug logging to see full details:

```bash
# In your .env
LOG_LEVEL=DEBUG
```

Or in Python:

```python
import logging
logging.getLogger("kytchen.api.routes.billing").setLevel(logging.DEBUG)
```

## Webhook Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `STRIPE_SECRET_KEY` | Stripe API secret key | `sk_test_...` or `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Webhook signing secret | `whsec_...` |
| `STRIPE_PRICE_CHEF` | Price ID for Chef ($35/mo) | `price_xxx` |
| `STRIPE_PRICE_SOUSCHEF` | Price ID for Sous Chef ($99/mo) | `price_yyy` |

### Production Webhook URL

Configure in Stripe Dashboard:
```
https://api.kytchen.dev/v1/billing/webhook
```

Events to listen for:
- `checkout.session.completed`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_failed`

## Troubleshooting

### 503 - Stripe not configured

Check that `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` are set.

### 400 - Missing stripe-signature header

The request must include the `stripe-signature` header. This is automatically added by Stripe when sending webhooks.

### 400 - Invalid signature

The webhook signature doesn't match. This can happen if:
- `STRIPE_WEBHOOK_SECRET` is wrong
- The request body was modified
- Using the wrong signing secret (live vs test)

### Workspace not found

The customer ID in the event doesn't match any workspace. This can happen with test events from `stripe trigger` since they use fake customer IDs.

## Security Notes

1. **Never expose webhook secrets** in logs or error messages
2. **Always verify signatures** before processing events
3. **Use HTTPS** in production
4. **Webhook endpoint is unauthenticated** - signature verification is the authentication

## Manual Testing Checklist

- [ ] `stripe login` succeeds
- [ ] `stripe listen --forward-to localhost:8000/v1/billing/webhook` connects
- [ ] `stripe trigger checkout.session.completed` returns 200
- [ ] `stripe trigger customer.subscription.updated` returns 200
- [ ] `stripe trigger customer.subscription.deleted` returns 200
- [ ] `stripe trigger invoice.payment_failed` returns 200
- [ ] Server logs show webhook processing
- [ ] Database records are created/updated correctly

#!/usr/bin/env python3
"""Create Stripe products and prices for Kytchen tiers.

Run this once to set up billing in your Stripe account.

Usage:
    STRIPE_SECRET_KEY=sk_live_... python scripts/setup_stripe_products.py
"""

import os
import stripe

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

if not stripe.api_key:
    print("Error: STRIPE_SECRET_KEY environment variable required")
    exit(1)

print("Creating Kytchen Stripe products...")
print(f"Using key: {stripe.api_key[:12]}...")

# Create Chef product ($35/mo)
chef_product = stripe.Product.create(
    name="Kytchen Chef",
    description="1 persistent line, 10GB storage, 100 req/min",
    metadata={"tier": "chef", "plan": "pro"},
)
print(f"Created product: {chef_product.name} ({chef_product.id})")

chef_price = stripe.Price.create(
    product=chef_product.id,
    unit_amount=3500,  # $35.00 in cents
    currency="usd",
    recurring={"interval": "month"},
    metadata={"tier": "chef", "plan": "pro"},
)
print(f"Created price: ${chef_price.unit_amount/100}/mo ({chef_price.id})")

# Create Sous Chef product ($99/mo)
souschef_product = stripe.Product.create(
    name="Kytchen Sous Chef",
    description="3 persistent lines, 50GB storage, 200 req/min",
    metadata={"tier": "souschef", "plan": "team"},
)
print(f"Created product: {souschef_product.name} ({souschef_product.id})")

souschef_price = stripe.Price.create(
    product=souschef_product.id,
    unit_amount=9900,  # $99.00 in cents
    currency="usd",
    recurring={"interval": "month"},
    metadata={"tier": "souschef", "plan": "team"},
)
print(f"Created price: ${souschef_price.unit_amount/100}/mo ({souschef_price.id})")

print("\n" + "="*60)
print("Add these to your .env files:")
print("="*60)
print(f"STRIPE_PRICE_CHEF={chef_price.id}")
print(f"STRIPE_PRICE_SOUSCHEF={souschef_price.id}")
print("="*60)

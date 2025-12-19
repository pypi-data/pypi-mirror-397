#!/usr/bin/env python3
"""
setup_stripe_products.py - Idempotently create or retrieve Stripe products/prices for metered billing.
This script ensures the "Compliance Check" metered product exists in Stripe.
"""

import os
import stripe

# Load Stripe API key
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
if not STRIPE_SECRET_KEY:
    print(
        "WARNING: STRIPE_SECRET_KEY not found in environment. Please set it to run this script."
    )
    # In a real scenario, we might exit, but for generation purposes, we allow import.
    # raise SystemExit("Error: STRIPE_SECRET_KEY must be set in environment.")
else:
    stripe.api_key = STRIPE_SECRET_KEY

# Configuration for the metered product
PRODUCT_NAME = "Compliance Check"
PRICE_LOOKUP_KEY = "compliance_check_meter"  # Unique key to identify the price
CURRENCY = "usd"
UNIT_AMOUNT = 50  # amount in cents, e.g., 50 cents ($0.50) per check
BILLING_INTERVAL = "month"  # interval for metered usage (typically 'month')


def setup():
    if not stripe.api_key:
        return

    # 1. Ensure product exists (create if not)
    product = None
    try:
        # Try to find an existing product by name (or by exact match via search if available)
        products = stripe.Product.list(active=True, limit=100)
        for p in products:
            if p.name == PRODUCT_NAME:
                product = p
                break
    except Exception as e:
        print(f"Warning: Could not list products ({e}). Assuming none exist.")
        product = None

    if product:
        print(f"Product '{PRODUCT_NAME}' already exists (id: {product.id})")
    else:
        try:
            product = stripe.Product.create(
                name=PRODUCT_NAME, description="On-demand compliance check (metered)"
            )
            print(f"Created product '{PRODUCT_NAME}' (id: {product.id})")
        except Exception as e:
            print(f"Error creating product: {e}")
            return

    # 2. Ensure metered price exists for the product
    price = None
    try:
        price = stripe.Price.retrieve(lookup_key=PRICE_LOOKUP_KEY)
        # If retrieve succeeds without error, we have an existing price
        print(
            f"Metered price for '{PRODUCT_NAME}' already exists (id: {price.id}, amount: {price.unit_amount} cents)"
        )
    except Exception:
        price = None  # Price not found or other error

    if not price:
        try:
            # Create a new metered recurring price for the product
            price = stripe.Price.create(
                product=product.id,
                unit_amount=UNIT_AMOUNT,
                currency=CURRENCY,
                recurring={"interval": BILLING_INTERVAL, "usage_type": "metered"},
                lookup_key=PRICE_LOOKUP_KEY,
                nickname="Compliance Check Metered Price",
            )
            print(
                f"Created new metered price (id: {price.id}) for '{PRODUCT_NAME}': ${UNIT_AMOUNT / 100:.2f} per use (billed {BILLING_INTERVAL})."
            )
        except Exception as e:
            print(f"Error creating price: {e}")

    # 3. Output summary
    print("---")
    print(f"Product: {product.name} (id: {product.id})")
    if price:
        cost = (
            f"${price.unit_amount / 100:.2f}"
            if price.unit_amount
            else f"{price.unit_amount}"
        )
        print(
            f"Price: {cost} per event (Price ID: {price.id}, usage_type: metered, billing interval: {BILLING_INTERVAL})"
        )
    else:
        print("No price was created or found for the product (check configuration).")


if __name__ == "__main__":
    setup()

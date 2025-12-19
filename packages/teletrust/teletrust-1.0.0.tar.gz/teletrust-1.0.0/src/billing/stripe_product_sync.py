"""
Stripe Product Sync - Automated Product & Price Management

Creates and updates Stripe Products and Prices for the 3-tier monetization model:
- Auditor (Free): Basic compliance checks
- Governor ($49/mo): Full compliance + metered usage
- Enterprise Shield ($299/mo): All features + priority support

Run this script to sync products to Stripe Dashboard:
    python -m src.billing.stripe_product_sync

Environment Variables Required:
    STRIPE_SECRET_KEY - Stripe API secret key
"""
import os
import stripe
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are set externally

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY
else:
    import warnings
    warnings.warn("STRIPE_SECRET_KEY not set. sync_all_products() will fail.")

# Product Definitions (source of truth)
PRODUCTS = {
    "auditor_free": {
        "name": "MOA Auditor",
        "description": "Basic compliance checks and audit packet preview. Free tier.",
        "metadata": {"tier": "free", "sku": "moa_auditor_free"},
        "prices": []  # Free tier has no price
    },
    "governor_monthly": {
        "name": "MOA Governor",
        "description": "Full compliance automation with metered usage billing.",
        "metadata": {"tier": "governor", "sku": "moa_governor_monthly"},
        "prices": [
            {
                "unit_amount": 4900,  # $49.00
                "currency": "usd",
                "recurring": {"interval": "month"},
                "lookup_key": "moa_governor_monthly",
            }
        ]
    },
    "enterprise_shield_monthly": {
        "name": "MOA Enterprise Shield",
        "description": "Complete compliance suite with priority support and SLA.",
        "metadata": {"tier": "enterprise", "sku": "moa_shield_monthly"},
        "prices": [
            {
                "unit_amount": 29900,  # $299.00
                "currency": "usd",
                "recurring": {"interval": "month"},
                "lookup_key": "moa_shield_monthly",
            }
        ]
    },
    "audit_pack_addon": {
        "name": "MOA Audit Pack (10-Pack)",
        "description": "Bundle of 10 audit packets. One-time purchase add-on.",
        "metadata": {"tier": "addon", "sku": "moa_audit_pack_10"},
        "prices": [
            {
                "unit_amount": 1499,  # $14.99 for 10 packs
                "currency": "usd",
                "recurring": None,  # One-time purchase
                "lookup_key": "moa_audit_pack_10",
            }
        ]
    },
}


def find_product_by_sku(sku: str) -> Optional[stripe.Product]:
    """Find existing product by SKU metadata."""
    products = stripe.Product.list(active=True, limit=100)
    for p in products.auto_paging_iter():
        if p.metadata.get("sku") == sku:
            return p
    return None


def find_price_by_lookup_key(lookup_key: str) -> Optional[stripe.Price]:
    """Find existing price by lookup key."""
    prices = stripe.Price.list(active=True, lookup_keys=[lookup_key], limit=1)
    if prices.data:
        return prices.data[0]
    return None


def sync_product(key: str, config: Dict[str, Any]) -> stripe.Product:
    """Create or update a Stripe product."""
    sku = config["metadata"]["sku"]
    existing = find_product_by_sku(sku)

    if existing:
        print(f"[SYNC] Updating product: {config['name']} (id={existing.id})")
        product = stripe.Product.modify(
            existing.id,
            name=config["name"],
            description=config["description"],
            metadata=config["metadata"],
        )
    else:
        print(f"[SYNC] Creating product: {config['name']}")
        product = stripe.Product.create(
            name=config["name"],
            description=config["description"],
            metadata=config["metadata"],
        )

    return product


def sync_price(product: stripe.Product, price_config: Dict[str, Any]) -> stripe.Price:
    """Create or update a Stripe price."""
    lookup_key = price_config["lookup_key"]
    existing = find_price_by_lookup_key(lookup_key)

    if existing:
        # Prices can't be updated, only archived. Check if config matches.
        if existing.unit_amount == price_config["unit_amount"]:
            print(f"[SYNC] Price unchanged: {lookup_key} (id={existing.id})")
            return existing
        else:
            print(f"[SYNC] Archiving old price: {lookup_key}")
            stripe.Price.modify(existing.id, active=False)

    print(f"[SYNC] Creating price: {lookup_key} (${price_config['unit_amount']/100:.2f})")

    price_params = {
        "product": product.id,
        "unit_amount": price_config["unit_amount"],
        "currency": price_config["currency"],
        "lookup_key": lookup_key,
        "transfer_lookup_key": True,
    }

    # Only add recurring if it's a subscription price
    if price_config.get("recurring"):
        price_params["recurring"] = price_config["recurring"]

    price = stripe.Price.create(**price_params)

    return price


def sync_all_products() -> Dict[str, Dict[str, Any]]:
    """Sync all products and prices to Stripe."""
    results = {}

    for key, config in PRODUCTS.items():
        product = sync_product(key, config)
        prices = []

        for price_config in config.get("prices", []):
            price = sync_price(product, price_config)
            prices.append({
                "id": price.id,
                "lookup_key": price_config["lookup_key"],
                "unit_amount": price.unit_amount,
            })

        results[key] = {
            "product_id": product.id,
            "name": product.name,
            "prices": prices,
        }

    return results


def create_checkout_url(lookup_key: str, customer_email: str, success_url: str, cancel_url: str) -> str:
    """Create a Stripe Checkout Session URL for a specific price."""
    price = find_price_by_lookup_key(lookup_key)
    if not price:
        raise ValueError(f"Price not found for lookup_key: {lookup_key}")

    # Determine mode based on recurring type
    mode = "subscription"
    if price.recurring and price.recurring.usage_type == "metered":
        mode = "subscription"  # Metered is still subscription mode

    session = stripe.checkout.Session.create(
        customer_email=customer_email,
        payment_method_types=["card"],
        line_items=[{"price": price.id, "quantity": 1 if price.recurring.usage_type != "metered" else None}],
        mode=mode,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return session.url


if __name__ == "__main__":
    print("=" * 60)
    print("MOA Stripe Product Sync")
    print("=" * 60)

    results = sync_all_products()

    print("\n" + "=" * 60)
    print("SYNC COMPLETE")
    print("=" * 60)

    for key, data in results.items():
        print(f"\n[{key}]")
        print(f"  Product ID: {data['product_id']}")
        print(f"  Name: {data['name']}")
        for p in data["prices"]:
            print(f"  Price: {p['lookup_key']} = ${p['unit_amount']/100:.2f} (id={p['id']})")

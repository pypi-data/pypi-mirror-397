"""Verify Stripe Products"""
import os
import stripe

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

print("=" * 60)
print("STRIPE PRODUCTS VERIFICATION")
print("=" * 60)

# List all products
products = stripe.Product.list(active=True, limit=50)
moa_products = [p for p in products.data if "moa" in (p.metadata.get("sku", "") or "").lower()]

print(f"\nFound {len(moa_products)} MOA products:\n")

for p in moa_products:
    tier = p.metadata.get("tier", "unknown").upper()
    print(f"[{tier}] {p.name}")
    print(f"  ID: {p.id}")
    print(f"  Description: {p.description[:60]}..." if len(p.description) > 60 else f"  Description: {p.description}")

    prices = stripe.Price.list(product=p.id, active=True)
    for price in prices.data:
        amt = price.unit_amount / 100 if price.unit_amount else 0
        billing = "one-time"
        if price.recurring:
            billing = f"{price.recurring.interval}ly subscription"
        print(f"  Price: ${amt:.2f} ({billing})")
        print(f"    Lookup Key: {price.lookup_key}")
    print()

print("=" * 60)
print("Creating test checkout URL for MOA Governor...")
print("=" * 60)

prices = stripe.Price.list(lookup_keys=["moa_governor_monthly"], limit=1)
if prices.data:
    price = prices.data[0]
    session = stripe.checkout.Session.create(
        customer_email="grzywajk@gmail.com",
        payment_method_types=["card"],
        line_items=[{"price": price.id, "quantity": 1}],
        mode="subscription",
        success_url="https://moa-telehealth.example.com/success",
        cancel_url="https://moa-telehealth.example.com/cancel",
    )
    print(f"\nCheckout URL (open in browser to test):\n{session.url}\n")
else:
    print("Governor price not found!")

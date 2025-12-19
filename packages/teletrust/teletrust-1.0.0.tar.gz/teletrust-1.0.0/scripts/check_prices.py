"""Verify Stripe Products - List all with prices"""
import os
import stripe

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

print("=" * 60)
print("STRIPE PRODUCTS")
print("=" * 60)

products = stripe.Product.list(active=True, limit=50)
for p in products.data:
    if "MOA" in p.name:
        prices = stripe.Price.list(product=p.id, active=True)
        price_str = "No price"
        for pr in prices.data:
            amt = pr.unit_amount / 100 if pr.unit_amount else 0
            period = ""
            if pr.recurring:
                period = f"/{pr.recurring.interval}"
            price_str = f"${amt:.2f}{period}"
        print(f"{p.name}: {price_str}")

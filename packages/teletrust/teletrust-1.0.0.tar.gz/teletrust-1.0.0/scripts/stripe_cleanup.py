"""
Stripe Catalog Cleanup & Validation
- Archive duplicates
- Archive products with no prices
- Test checkout for each valid product
"""
import os
import stripe

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

print("=" * 60)
print("STRIPE CATALOG AUDIT & CLEANUP")
print("=" * 60)

# 1. Get all products
products = stripe.Product.list(active=True, limit=100)
product_data = []

for p in products.data:
    prices = stripe.Price.list(product=p.id, active=True, limit=10)
    price_list = []
    for pr in prices.data:
        amt = pr.unit_amount / 100 if pr.unit_amount else 0
        recurring = ""
        if pr.recurring:
            recurring = f"/{pr.recurring.interval}"
        price_list.append({
            "id": pr.id,
            "amount": amt,
            "recurring": recurring,
            "display": f"${amt:.2f}{recurring}"
        })

    product_data.append({
        "id": p.id,
        "name": p.name,
        "prices": price_list,
        "has_price": len(price_list) > 0,
        "metadata": p.metadata or {}
    })

# 2. Identify issues
print("\n[AUDIT] Products with issues:")
duplicates = {}
for p in product_data:
    name = p["name"]
    if name not in duplicates:
        duplicates[name] = []
    duplicates[name].append(p)

to_archive = []

# Products with no prices
for p in product_data:
    if not p["has_price"]:
        print(f"  ❌ NO PRICE: {p['name']} ({p['id']})")
        to_archive.append(p["id"])

# Duplicate products (keep first, archive rest)
for name, prods in duplicates.items():
    if len(prods) > 1:
        print(f"  ⚠️  DUPLICATE ({len(prods)}x): {name}")
        for i, p in enumerate(prods):
            if i == 0:
                print(f"      KEEP: {p['id']} (prices: {len(p['prices'])})")
            else:
                print(f"      ARCHIVE: {p['id']} (prices: {len(p['prices'])})")
                to_archive.append(p["id"])

# 3. Archive problematic products
print(f"\n[CLEANUP] Archiving {len(to_archive)} products...")
for pid in to_archive:
    try:
        stripe.Product.modify(pid, active=False)
        print(f"  Archived: {pid}")
    except Exception as e:
        print(f"  Failed to archive {pid}: {e}")

# 4. Final catalog
print("\n" + "=" * 60)
print("FINAL CATALOG (Active Products)")
print("=" * 60)

products = stripe.Product.list(active=True, limit=100)
valid_products = []

for p in products.data:
    prices = stripe.Price.list(product=p.id, active=True, limit=10)
    if prices.data:
        price = prices.data[0]
        amt = price.unit_amount / 100 if price.unit_amount else 0
        recurring = ""
        if price.recurring:
            recurring = f"/{price.recurring.interval}"
        print(f"✅ {p.name}: ${amt:.2f}{recurring} (price: {price.id})")
        valid_products.append({
            "name": p.name,
            "product_id": p.id,
            "price_id": price.id,
            "amount": amt,
            "recurring": recurring
        })

# 5. Create test checkout sessions
print("\n" + "=" * 60)
print("TEST CHECKOUT URLS (as customer)")
print("=" * 60)

for prod in valid_products:
    try:
        price = stripe.Price.retrieve(prod["price_id"])
        mode = "subscription" if price.recurring else "payment"

        session = stripe.checkout.Session.create(
            customer_email="test@example.com",
            payment_method_types=["card"],
            line_items=[{"price": prod["price_id"], "quantity": 1}],
            mode=mode,
            success_url="https://example.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://example.com/cancel",
            metadata={"product_name": prod["name"]}
        )
        print(f"\n{prod['name']}: ${prod['amount']:.2f}{prod['recurring']}")
        print(f"  Mode: {mode}")
        print(f"  Checkout: {session.url[:80]}...")
    except Exception as e:
        print(f"\n❌ {prod['name']}: FAILED - {e}")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)

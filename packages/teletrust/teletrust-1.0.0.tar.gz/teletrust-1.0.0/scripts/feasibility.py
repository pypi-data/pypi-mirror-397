"""
FEASIBILITY ANALYSIS - Which products can actually make money?
Tests each product and rates feasibility
"""
import os
import stripe

try:
    from dotenv import load_dotenv
    load_dotenv()
except: pass

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

print("=" * 70)
print("REVENUE FEASIBILITY ANALYSIS")
print("=" * 70)

products = stripe.Product.list(active=True, limit=100)

analysis = []

for p in products.data:
    prices = stripe.Price.list(product=p.id, active=True, limit=1)
    if not prices.data:
        continue

    price = prices.data[0]
    amt = price.unit_amount / 100 if price.unit_amount else 0
    is_subscription = bool(price.recurring)
    interval = price.recurring.interval if price.recurring else "one-time"

    # Feasibility scoring
    score = 0
    issues = []
    strengths = []

    # Price point analysis
    if amt < 10:
        score += 1
        strengths.append("Low friction entry price")
    elif amt <= 50:
        score += 2
        strengths.append("Sweet spot pricing ($29-49)")
    elif amt <= 100:
        score += 1
        strengths.append("Mid-tier acceptable")
    else:
        score += 0
        issues.append(f"High price (${amt}) needs demo/trial")

    # Recurring = MRR
    if is_subscription:
        score += 2
        strengths.append("Recurring revenue")
    else:
        score += 1
        issues.append("One-time only, no MRR")

    # Product name clarity
    clear_names = ["Governor", "Auditor", "Writer", "Guard"]
    if any(n in p.name for n in clear_names):
        score += 1
        strengths.append("Clear value proposition in name")
    else:
        issues.append("Vague product name")

    # Description quality
    if p.description and len(p.description) > 50:
        score += 1
        strengths.append("Good description")
    else:
        issues.append("Weak/missing description")

    # Market fit (telehealth compliance is hot)
    if any(x in p.name.lower() for x in ["telehealth", "compliance", "audit", "consent"]):
        score += 2
        strengths.append("Hot market (telehealth/compliance)")

    # Calculate feasibility
    feasibility = min(score / 9, 1.0)  # Normalize to 0-1

    # Revenue potential
    if is_subscription:
        rev_50 = amt * 50  # 50 customers MRR
        rev_200 = amt * 200  # 200 customers MRR
    else:
        rev_50 = amt * 50 * 0.3  # 30% repeat rate
        rev_200 = amt * 200 * 0.3

    analysis.append({
        "name": p.name,
        "price": amt,
        "interval": interval,
        "feasibility": feasibility,
        "score": score,
        "strengths": strengths,
        "issues": issues,
        "mrr_50": rev_50,
        "mrr_200": rev_200,
        "product_id": p.id,
        "price_id": price.id
    })

# Sort by feasibility
analysis.sort(key=lambda x: x["feasibility"], reverse=True)

print("\n🎯 TOP MONEY MAKERS (Ranked by Feasibility)\n")

for i, a in enumerate(analysis[:5], 1):
    emoji = "🟢" if a["feasibility"] >= 0.7 else "🟡" if a["feasibility"] >= 0.5 else "🔴"
    print(f"{emoji} #{i}: {a['name']}")
    print(f"   Price: ${a['price']:.2f}/{a['interval']}")
    print(f"   Feasibility: {a['feasibility']:.0%}")
    print(f"   MRR @ 50 customers: ${a['mrr_50']:,.0f}")
    print(f"   MRR @ 200 customers: ${a['mrr_200']:,.0f}")
    print(f"   Strengths: {', '.join(a['strengths'])}")
    if a["issues"]:
        print(f"   Issues: {', '.join(a['issues'])}")
    print()

print("=" * 70)
print("ACTION PLAN - START HERE")
print("=" * 70)

top = analysis[0] if analysis else None
if top:
    print(f"""
🚀 FOCUS ON: {top['name']} (${top['price']}/{top['interval']})

1. CREATE CHECKOUT LINK NOW:
   https://checkout.stripe.com

2. SHARE WITH 10 PEOPLE TODAY:
   - LinkedIn post with checkout link
   - Email 5 PMHNPs you know
   - DM 5 telehealth practitioners

3. FIRST $500 MRR MATH:
   {top['price']}/mo × {int(500/top['price'])} customers = $500 MRR

4. TEST CHECKOUT:
""")

    # Create actual checkout session
    session = stripe.checkout.Session.create(
        customer_email="test@example.com",
        payment_method_types=["card"],
        line_items=[{"price": top["price_id"], "quantity": 1}],
        mode="subscription" if top["interval"] != "one-time" else "payment",
        success_url="https://your-app.com/success",
        cancel_url="https://your-app.com/cancel",
    )
    print(f"   Checkout URL: {session.url}")

print("\n" + "=" * 70)
print("PRODUCTS TO ARCHIVE (Low Feasibility)")
print("=" * 70)
for a in analysis[-3:]:
    print(f"🔴 {a['name']} - Feasibility: {a['feasibility']:.0%}")
    print(f"   Issues: {', '.join(a['issues'])}")

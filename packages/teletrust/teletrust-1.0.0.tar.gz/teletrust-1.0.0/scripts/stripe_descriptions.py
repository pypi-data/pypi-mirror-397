"""
Stripe Product Description Updates - Make Products Sellable
"""
import os
import stripe

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")

# Product descriptions that sell
PRODUCT_UPDATES = {
    "MOA Audit Pack (10-Pack)": {
        "description": "10 compliance audit packets. Each packet includes: risk assessment, consent checklist, and documentation verification. Perfect for small clinics."
    },
    "MOA Governor": {
        "description": "Full telehealth compliance automation. Includes: consent validation, POS/modifier checks, audit packet generation, and denial risk scanning. $49/month flat."
    },
    "MOA Auditor": {
        "description": "Basic compliance checking for solo practitioners. Consent review, basic documentation checks, and simple audit reports. Start free, upgrade anytime."
    },
    "MOA Enterprise Shield": {
        "description": "Complete compliance suite with SLA support. Everything in Governor plus: priority support, custom rule sets, and dedicated account manager."
    },
    "Telehealth Governor API": {
        "description": "Enterprise API access for EHR integration. RESTful endpoints for consent validation, compliance checking, and audit packet generation. Includes 10,000 API calls/month."
    },
    "APA Writer": {
        "description": "Academic writing assistant with APA-7 formatting. Auto-corrects citations, checks formatting, and improves readability. Perfect for MSN/DNP students."
    },
    "Writer Guard": {
        "description": "Writing quality protection. Detects keyboard mashing, bot text, and low-effort submissions using spectral analysis. Ideal for educators."
    },
    "ESM Rhythm (token delta)": {
        "description": "Token usage analytics and optimization. Track your LLM costs, visualize token patterns, and optimize prompts for cost savings."
    },
    "Esm": {
        "description": "Ephemerality State Machine - Memory management for AI agents. Automatic decay, context packing, and session persistence."
    },
}

print("=" * 60)
print("UPDATING PRODUCT DESCRIPTIONS")
print("=" * 60)

products = stripe.Product.list(active=True, limit=100)
for p in products.data:
    if p.name in PRODUCT_UPDATES:
        update = PRODUCT_UPDATES[p.name]
        try:
            stripe.Product.modify(p.id, description=update["description"])
            print(f"✅ Updated: {p.name}")
        except Exception as e:
            print(f"❌ Failed: {p.name} - {e}")

print("\nDone!")

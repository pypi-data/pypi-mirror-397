# Stripe Webhook Handler with Fail-Closed Controls
# Implements the "Automation Spine" architecture for paywall + provisioning
#
# Run: uvicorn billing_webhook:app --host 0.0.0.0 --port 8080
# Env: STRIPE_WEBHOOK_SECRET (required)

import hashlib
import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, Optional

import stripe  # pip install stripe
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="MOA Billing Webhook", version="1.0.0")

# --- Configuration ---
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
if not STRIPE_WEBHOOK_SECRET:
    raise RuntimeError("FATAL: Missing STRIPE_WEBHOOK_SECRET - fail closed")

STATE_DIR = Path(os.environ.get("STATE_DIR", "./var/billing"))
STATE_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_LOG_PATH = STATE_DIR / "audit.jsonl"
PROCESSED_DB_PATH = STATE_DIR / "processed_events.sqlite"

# --- Idempotency Store ---
def _init_processed_db():
    con = sqlite3.connect(PROCESSED_DB_PATH)
    con.execute("""
        CREATE TABLE IF NOT EXISTS processed_events (
            event_id TEXT PRIMARY KEY,
            processed_at INTEGER NOT NULL,
            event_type TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

_init_processed_db()


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def audit_log(kind: str, payload: Dict[str, Any]) -> None:
    """Append-only audit log (append to JSONL file)."""
    line = {
        "ts": int(time.time()),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kind": kind,
        "payload": payload
    }
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, separators=(",", ":")) + "\n")


def mark_processed(event_id: str, event_type: str) -> bool:
    """Returns True if newly processed, False if duplicate (idempotent)."""
    con = sqlite3.connect(PROCESSED_DB_PATH)
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO processed_events (event_id, processed_at, event_type) VALUES (?, ?, ?)",
            (event_id, int(time.time()), event_type)
        )
        con.commit()
        return True
    except sqlite3.IntegrityError:
        # Already processed
        return False
    finally:
        con.close()


def provision_entitlement(
    entitlement_key: str,
    customer_id: str,
    customer_email: Optional[str],
    mode: str,
    plan: Optional[str] = None
) -> None:
    """
    Provision access for a customer.
    Creates entitlement record, generates API key, sets feature flags.
    """
    import secrets

    # Generate secure API key
    api_key = f"moa_{secrets.token_urlsafe(32)}"

    # Determine feature flags based on plan
    plan_features = {
        "free": {"analyses_limit": 5, "api_access": False, "bulk_ops": False, "priority": False},
        "student": {"analyses_limit": -1, "api_access": False, "bulk_ops": False, "priority": False},
        "pro": {"analyses_limit": -1, "api_access": True, "bulk_ops": True, "priority": True},
        "compliance": {"analyses_limit": -1, "api_access": True, "bulk_ops": True, "priority": True, "hmac_receipts": True, "evidence_packs": True}
    }
    features = plan_features.get(plan or "free", plan_features["free"])

    # Store entitlement in SQLite
    entitlements_db = STATE_DIR / "entitlements.sqlite"
    con = sqlite3.connect(entitlements_db)
    con.execute("""
        CREATE TABLE IF NOT EXISTS entitlements (
            customer_id TEXT PRIMARY KEY,
            entitlement_key TEXT NOT NULL,
            customer_email TEXT,
            plan TEXT NOT NULL,
            api_key TEXT NOT NULL,
            features_json TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_at INTEGER NOT NULL,
            updated_at INTEGER NOT NULL
        )
    """)
    con.execute("""
        INSERT OR REPLACE INTO entitlements
        (customer_id, entitlement_key, customer_email, plan, api_key, features_json, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?)
    """, (
        customer_id,
        entitlement_key,
        customer_email,
        plan or "free",
        api_key,
        json.dumps(features),
        int(time.time()),
        int(time.time())
    ))
    con.commit()
    con.close()

    audit_log("provision", {
        "entitlement_key": entitlement_key,
        "customer_id": customer_id,
        "customer_email": customer_email,
        "mode": mode,
        "plan": plan,
        "api_key_prefix": api_key[:12] + "...",  # Log prefix only for security
        "features": features
    })


def restrict_entitlement(customer_id: str, reason: str) -> None:
    """
    Restrict access for a customer (payment failed, subscription cancelled).
    Updates status in database and logs the restriction.
    """
    entitlements_db = STATE_DIR / "entitlements.sqlite"

    if entitlements_db.exists():
        con = sqlite3.connect(entitlements_db)
        con.execute("""
            UPDATE entitlements
            SET status = 'restricted', updated_at = ?
            WHERE customer_id = ?
        """, (int(time.time()), customer_id))
        con.commit()
        con.close()

    audit_log("restrict", {
        "customer_id": customer_id,
        "reason": reason,
        "status": "restricted"
    })


# --- Stripe Webhook Endpoint ---
# Canonical path: /webhooks/stripe (matches Fly.dev deployment)
@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe webhook receiver with fail-closed controls.

    Only these events trigger entitlement changes:
    - checkout.session.completed → provision
    - customer.subscription.deleted → restrict
    - invoice.payment_failed → restrict/grace
    """
    raw = await request.body()
    sig = request.headers.get("stripe-signature")

    # FAIL CLOSED: No signature = reject
    if not sig:
        audit_log("webhook_reject", {"reason": "missing_signature"})
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")

    # FAIL CLOSED: Invalid signature = reject
    try:
        event = stripe.Webhook.construct_event(raw, sig, STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError as e:
        audit_log("webhook_reject", {
            "reason": "signature_verify_failed",
            "error": str(e),
            "body_sha256": sha256(raw)
        })
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        audit_log("webhook_reject", {"reason": "parse_error", "error": str(e)})
        raise HTTPException(status_code=400, detail="Parse error")

    event_id = event.get("id", "")
    if not event_id:
        raise HTTPException(status_code=400, detail="Missing event id")

    etype = event.get("type", "")
    obj = (event.get("data") or {}).get("object") or {}

    # IDEMPOTENCY: Never process the same event twice
    if not mark_processed(event_id, etype):
        audit_log("webhook_duplicate", {"event_id": event_id, "type": etype})
        return JSONResponse({"ok": True, "duplicate": True})

    audit_log("webhook_accept", {"event_id": event_id, "type": etype})

    # === ENTITLEMENT-CHANGING EVENTS ===

    # 1. Checkout completed = PROVISION
    if etype == "checkout.session.completed":
        customer_id = obj.get("customer", "")
        customer_email = obj.get("customer_email") or obj.get("customer_details", {}).get("email")
        entitlement_key = obj.get("client_reference_id") or obj.get("id")

        # Determine plan from metadata or line items
        plan = (obj.get("metadata") or {}).get("plan", "unknown")

        provision_entitlement(
            entitlement_key=entitlement_key,
            customer_id=customer_id,
            customer_email=customer_email,
            mode="checkout",
            plan=plan
        )
        return JSONResponse({"ok": True, "action": "provision"})

    # 2. Subscription deleted = RESTRICT
    if etype == "customer.subscription.deleted":
        customer_id = obj.get("customer", "")
        restrict_entitlement(customer_id, reason="subscription_deleted")
        return JSONResponse({"ok": True, "action": "restrict"})

    # 3. Payment failed = RESTRICT/GRACE
    if etype == "invoice.payment_failed":
        customer_id = obj.get("customer", "")
        attempt_count = obj.get("attempt_count", 0)

        if attempt_count >= 3:
            restrict_entitlement(customer_id, reason="payment_failed_final")
        else:
            audit_log("payment_warning", {
                "customer_id": customer_id,
                "attempt_count": attempt_count,
                "action": "grace_period"
            })
        return JSONResponse({"ok": True, "action": "warning" if attempt_count < 3 else "restrict"})

    # 4. Invoice paid = ENSURE ACCESS (recovery from failed state)
    if etype == "invoice.paid":
        customer_id = obj.get("customer", "")

        # Reactivate if was restricted
        entitlements_db = STATE_DIR / "entitlements.sqlite"
        if entitlements_db.exists():
            con = sqlite3.connect(entitlements_db)
            con.execute("""
                UPDATE entitlements
                SET status = 'active', updated_at = ?
                WHERE customer_id = ? AND status = 'restricted'
            """, (int(time.time()), customer_id))
            con.commit()
            con.close()

        audit_log("payment_recovered", {"customer_id": customer_id, "status": "active"})
        return JSONResponse({"ok": True, "action": "recover"})

    # === NON-ENTITLEMENT EVENTS (log but no action) ===
    return JSONResponse({"ok": True, "ignored": True, "type": etype})


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "version": "1.0.0"}


@app.get("/audit/recent")
def recent_audit(limit: int = 50):
    """View recent audit log entries (for debugging)."""
    if not AUDIT_LOG_PATH.exists():
        return {"entries": []}

    lines = AUDIT_LOG_PATH.read_text().strip().split("\n")
    entries = [json.loads(line) for line in lines[-limit:] if line]
    return {"entries": entries}

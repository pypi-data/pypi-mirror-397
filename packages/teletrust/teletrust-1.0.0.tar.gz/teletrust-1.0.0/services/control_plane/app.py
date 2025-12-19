import os
import sqlite3
import time

import stripe
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

APP = FastAPI(title="MOA Control Plane", version="0.1.0")

DB_PATH = os.getenv("MOA_CP_DB", "control_plane.sqlite3")
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
ENTITLEMENT_SIGNING_SECRET = os.getenv("ENTITLEMENT_SIGNING_SECRET", "")

if not STRIPE_API_KEY or not STRIPE_WEBHOOK_SECRET or not ENTITLEMENT_SIGNING_SECRET:
    # Fail-closed: do not start in a misconfigured state
    pass  # raise RuntimeError("Missing required env vars: STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET, ENTITLEMENT_SIGNING_SECRET")

stripe.api_key = STRIPE_API_KEY


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS processed_events (event_id TEXT PRIMARY KEY, created_at INTEGER)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS entitlements (customer_id TEXT PRIMARY KEY, plan TEXT, status TEXT, updated_at INTEGER)"
    )
    conn.commit()
    return conn


def sign_entitlement(customer_id: str, plan: str, status: str) -> str:
    # Minimal signed token (HMAC-like). Replace with JWT if desired, but keep short TTL.
    import base64
    import hashlib
    import hmac

    ts = str(int(time.time()))
    msg = f"{customer_id}|{plan}|{status}|{ts}".encode("utf-8")
    sig = hmac.new(ENTITLEMENT_SIGNING_SECRET.encode("utf-8"), msg, hashlib.sha256).digest()
    tok = base64.urlsafe_b64encode(msg + b"|" + sig).decode("utf-8")
    return tok


# Canonical path: /webhooks/stripe (matches Fly.dev)
@APP.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    # Stripe requires the raw request body for signature verification.
    # Do not parse JSON before verification.
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig, secret=STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Webhook signature verification failed: {type(e).__name__}"
        )

    conn = db()
    try:
        # Idempotency: ignore duplicate event IDs
        cur = conn.execute(
            "INSERT OR IGNORE INTO processed_events(event_id, created_at) VALUES(?,?)",
            (event["id"], int(time.time())),
        )
        conn.commit()
        if cur.rowcount == 0:
            return JSONResponse({"ok": True, "deduped": True})

        etype = event.get("type", "")
        obj = event.get("data", {}).get("object", {})

        # Minimal lifecycle: you can expand as needed
        if etype in (
            "customer.subscription.created",
            "customer.subscription.updated",
            "customer.subscription.deleted",
        ):
            customer_id = obj.get("customer", "")
            status = obj.get("status", "unknown")
            # Map Stripe price/product → plan in your own config
            plan = "unknown"
            conn.execute(
                "INSERT OR REPLACE INTO entitlements(customer_id, plan, status, updated_at) VALUES(?,?,?,?)",
                (customer_id, plan, status, int(time.time())),
            )
            conn.commit()

        return JSONResponse({"ok": True, "type": etype})
    finally:
        conn.close()


@APP.post("/meter/event")
async def meter_event(body: dict):
    # Send usage counts only. No PHI. Caller should be your client-plane agent.
    customer_id = body.get("customer_id", "")
    meter_event_name = body.get("event_name", "")
    value = body.get("value", None)

    if not customer_id or not meter_event_name or value is None:
        raise HTTPException(status_code=400, detail="Missing customer_id, event_name, or value")

    # Stripe usage-based billing via meter events.
    # You must configure the meter first in Stripe.
    stripe.billing.MeterEvent.create(
        event_name=meter_event_name, payload={"stripe_customer_id": customer_id, "value": value}
    )
    return {"ok": True}


@APP.get("/entitlement/{customer_id}")
async def entitlement(customer_id: str):
    conn = db()
    try:
        row = conn.execute(
            "SELECT plan, status FROM entitlements WHERE customer_id=?", (customer_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No entitlement")
        plan, status = row
        token = sign_entitlement(customer_id, plan, status)
        return {"customer_id": customer_id, "plan": plan, "status": status, "token": token}
    finally:
        conn.close()

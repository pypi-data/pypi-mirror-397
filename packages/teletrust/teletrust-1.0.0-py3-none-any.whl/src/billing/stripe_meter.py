# Local-first Usage Metering with Optional Stripe
# Always writes local NDJSON; optionally sends Stripe meter events.

from __future__ import annotations
import os
import json
import time
import uuid
from typing import Any, Dict, Optional
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Configuration from environment
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_METER_EVENT_NAME = os.getenv("STRIPE_METER_EVENT_NAME", "moa_usage")
STRIPE_CUSTOMER_ID = os.getenv("STRIPE_CUSTOMER_ID", "")

# Default local storage
DEFAULT_EVENTS_PATH = Path("./var/usage_events.ndjson")


def emit_local_event(
    kind: str,
    payload: Dict[str, Any],
    out_path: Optional[Path] = None
) -> str:
    """
    Always writes event to local NDJSON file (never fails).

    Returns:
        Event ID (UUID)
    """
    path = out_path or DEFAULT_EVENTS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "ts": int(time.time()),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "id": str(uuid.uuid4()),
        "kind": kind,
        "payload": payload
    }

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")

    return event["id"]


def emit_stripe_meter_event(
    value: int,
    customer_id: Optional[str] = None,
    identifier: Optional[str] = None
) -> Dict[str, Any]:
    """
    Sends a Stripe Billing Meter Event (v1) if configured.

    Requires:
      - STRIPE_SECRET_KEY
      - STRIPE_CUSTOMER_ID (or customer_id param)
      - STRIPE_METER_EVENT_NAME (must match an active Stripe meter's event_name)

    Docs: https://docs.stripe.com/api/billing/meter-event/create

    Returns:
        Stripe API response dict, or {"skipped": True} if not configured
    """
    if not STRIPE_SECRET_KEY:
        return {"skipped": True, "reason": "STRIPE_SECRET_KEY not set"}

    if not REQUESTS_AVAILABLE:
        return {"skipped": True, "reason": "requests library not installed"}

    cid = customer_id or STRIPE_CUSTOMER_ID
    if not cid:
        return {"skipped": True, "reason": "No customer_id provided"}

    if value <= 0:
        return {"skipped": True, "reason": "value must be positive"}

    ident = identifier or str(uuid.uuid4())

    url = "https://api.stripe.com/v1/billing/meter_events"
    data = {
        "event_name": STRIPE_METER_EVENT_NAME,
        "identifier": ident,
        "timestamp": int(time.time()),
        "payload[stripe_customer_id]": cid,
        "payload[value]": str(value),
    }

    try:
        r = requests.post(url, data=data, auth=(STRIPE_SECRET_KEY, ""), timeout=20)
        if r.status_code >= 400:
            return {"error": True, "status": r.status_code, "body": r.text[:500]}
        return r.json()
    except Exception as e:
        return {"error": True, "exception": str(e)}


def record_usage(
    kind: str,
    value: int = 1,
    metadata: Optional[Dict[str, Any]] = None,
    customer_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    High-level function: always logs locally, optionally sends to Stripe.

    Args:
        kind: Event type (e.g., 'audit_run', 'compliance_check')
        value: Quantity for Stripe metering (default 1)
        metadata: Additional data to log locally
        customer_id: Override STRIPE_CUSTOMER_ID

    Returns:
        Dict with local_event_id and stripe response
    """
    payload = metadata or {}
    payload["value"] = value

    # Always local
    local_id = emit_local_event(kind, payload)

    # Optionally Stripe
    stripe_result = None
    if STRIPE_SECRET_KEY and (customer_id or STRIPE_CUSTOMER_ID):
        stripe_result = emit_stripe_meter_event(
            value=value,
            customer_id=customer_id,
            identifier=local_id
        )

    return {
        "local_event_id": local_id,
        "stripe": stripe_result
    }


# Export
__all__ = [
    "emit_local_event",
    "emit_stripe_meter_event",
    "record_usage"
]

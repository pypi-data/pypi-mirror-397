
import json
import os
import time
import hashlib
import uuid
import requests
import threading
from typing import Dict, Any, Optional

# Optional: Load Stripe config from env
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_METER_EVENT_NAME = os.getenv("STRIPE_METER_EVENT_NAME", "moa_usage")
STRIPE_CUSTOMER_ID = os.getenv("STRIPE_CUSTOMER_ID", "")

class MoaUsageLedger:
    """
    Append-only, hash-chained ledger for usage events.
    Ensures integrity of billing data.
    """
    def __init__(self, ledger_path: str = "usage_ledger.jsonl", stripe_enabled: bool = True):
        self.ledger_path = ledger_path
        self.stripe_enabled = stripe_enabled and bool(STRIPE_SECRET_KEY)
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.ledger_path):
            with open(self.ledger_path, "w") as f:
                pass # Create empty file

    def _get_last_hash(self) -> str:
        last_hash = "0" * 64 # Genesis hash
        try:
            with open(self.ledger_path, "r") as f:
                lines = f.readlines()
                if lines:
                    last_entries = [json.loads(line) for line in lines if line.strip()]
                    if last_entries:
                        last_hash = last_entries[-1].get("hash", last_hash)
        except Exception as e:
            print(f"WARN: Error reading ledger: {e}")
        return last_hash

    def record_event(self, event_name: str, quantity: int = 1, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Record a usage event to the ledger.
        """
        if metadata is None:
            metadata = {}

        timestamp = time.time()
        event_id = str(uuid.uuid4())

        with self._lock:
            prev_hash = self._get_last_hash()

            # Payload to hash: event specifics + previous hash
            payload = {
                "id": event_id,
                "timestamp": timestamp,
                "event": event_name,
                "quantity": quantity,
                "metadata": metadata,
                "prev_hash": prev_hash
            }

            # Calculate Hash
            # Canonicalize by dumping keys sorted
            payload_str = json.dumps(payload, sort_keys=True)
            curr_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

            record = payload.copy()
            record["hash"] = curr_hash

            # Append to file
            with open(self.ledger_path, "a") as f:
                f.write(json.dumps(record) + "\n")

        # Emit to Stripe if configured
        if self.stripe_enabled:
            self._emit_stripe(record)

        return record

    def _emit_stripe(self, record: Dict[str, Any]) -> None:
        """
        Best-effort asynchronous-like emission to Stripe.
        In a real prod environment, this should be offloaded to a queue.
        Here we do synchronous with timeout for fail-open billing (don't block gov).
        """
        # Determine customer ID from metadata or env
        cid = record["metadata"].get("customer_id") or STRIPE_CUSTOMER_ID
        if not cid:
            return

        try:
            url = "https://api.stripe.com/v1/billing/meter_events"
            data = {
                "event_name": STRIPE_METER_EVENT_NAME,
                "identifier": record["id"], # Idempotency key
                "timestamp": int(record["timestamp"]),
                "payload[stripe_customer_id]": cid,
                "payload[value]": str(record["quantity"]),
            }
            # Short timeout to avoid latency impact
            requests.post(url, data=data, auth=(STRIPE_SECRET_KEY, ""), timeout=2.0)
        except Exception as e:
            # We log but don't crash - billing failure shouldn't stop governance
            # In prod, write to a "failed_billing.log" for retry
            print(f"WARN: Stripe emit failed: {e}")

    def verify_integrity(self) -> bool:
        """
        Verify the hash chain of the ledger.
        """
        try:
            with open(self.ledger_path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return True # Empty is valid

        prev_hash = "0" * 64
        for i, line in enumerate(lines):
            if not line.strip(): continue
            try:
                record = json.loads(line)
                stored_hash = record.pop("hash")

                # Verify prev_hash link
                if record["prev_hash"] != prev_hash:
                    print(f"FAIL at line {i+1}: prev_hash mismatch.")
                    return False

                # Verify current hash
                payload_str = json.dumps(record, sort_keys=True)
                calc_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

                if calc_hash != stored_hash:
                    print(f"FAIL at line {i+1}: Hash invalid.")
                    return False

                prev_hash = stored_hash
            except Exception as e:
                print(f"FAIL at line {i+1}: Malformed record. {e}")
                return False

        return True

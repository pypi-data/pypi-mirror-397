
import os
import json
import requests
from typing import List, Dict, Any

class StripeMetersExporter:
    """
    Exports events from MoaUsageLedger to Stripe Billing Meters.
    """
    def __init__(self, ledger_path: str = "usage_ledger.jsonl", stripe_key: str = None):
        self.ledger_path = ledger_path
        self.api_key = stripe_key or os.environ.get("STRIPE_SECRET_KEY")
        self.api_url = "https://api.stripe.com/v1/billing/meter_events"

    def export_new_events(self, customer_id: str = "cus_TEST123"): # Default for dev
        """
        Read ledger and export events.
        In a real prod system, this would track 'last_exported_offset'.
        For MVP/Nightly, we can try to push recently added or all, relying on idempotency.
        Stripe limits throughput, so batching might be needed for high volume.
        """
        if not self.api_key:
            print("WARN: No STRIPE_SECRET_KEY provided. Skipping export.")
            return

        print(f"Exporting events from {self.ledger_path}...")

        try:
            with open(self.ledger_path, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print("Ledger not found.")
            return

        count = 0
        for line in lines:
            if not line.strip(): continue
            record = json.loads(line)

            # Map Ledger Event -> Stripe Payload
            payload = {
                "event_name": record["event"],
                "timestamp": int(record["timestamp"]),
                "payload": {
                    "stripe_customer_id": customer_id,
                    "value": str(record["quantity"])
                },
                "identifier": record["id"] # Idempotency Key from Ledger
            }

            # Post to Stripe
            try:
                resp = requests.post(
                    self.api_url,
                    auth=(self.api_key, ""),
                    data={
                        "event_name": payload["event_name"],
                        "timestamp": payload["timestamp"],
                        "payload[stripe_customer_id]": payload["payload"]["stripe_customer_id"],
                        "payload[value]": payload["payload"]["value"],
                        "identifier": payload["identifier"]
                    }
                )

                if resp.status_code in [200, 201, 202]: # 202 is common for async
                    # print(f"Exported {record['id']}")
                    count += 1
                elif resp.status_code == 400 and "idempotency" in resp.text.lower():
                    # Duplicate, skip
                    print(f"[INFO] Skipping duplicate event {payload['identifier']} (Idempotency)")
                else:
                    print(f"Error exporting {record['id']}: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"Network error on {record['id']}: {e}")

        print(f"Exported {count} events to Stripe.")

if __name__ == "__main__":
    exporter = StripeMetersExporter()
    exporter.export_new_events()

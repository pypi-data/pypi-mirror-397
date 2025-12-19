#!/usr/bin/env python3
"""
AB 688 Audit Tool - Telehealth Utilization Anomaly Detection
============================================================
This script analyzes the usage ledger using the ESM Rhythm Engine
to detect anomalies in telehealth utilization data, as required
by California AB 688 (Telehealth for All Act of 2025).

It maps ledger events to the ESM spectral graph and flags
deviations from the "normal" rhythm (baseline).
"""

import sys
import json
import os
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).parent.resolve()
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

from src.esm.core import create_healthcare_esm


def analyze_ledger(ledger_path: str):
    print(f"[*] Loading ledger: {ledger_path}")
    if not os.path.exists(ledger_path):
        print("[!] Ledger file not found.")
        return

    esm = create_healthcare_esm()
    anomalies = []
    total_events = 0

    print("[*] Initializing ESM Rhythm Engine...")
    print(f"    Nodes: {esm.n_nodes}")
    print(f"    Mode Threshold: {esm.config.global_mode_threshold}")

    with open(ledger_path, "r") as f:
        for line in f:
            try:
                record = json.loads(line)
                event_type = record.get("event")
                metadata = record.get("metadata", {})
                verdict = metadata.get("verdict")

                # Map Ledger -> ESM Event
                esm_event = "ALL_GOOD"  # Default

                if event_type == "telehealth_policy_eval":
                    if verdict == "ALLOW":
                        esm_event = "ALL_GOOD"
                    elif verdict == "DENY":
                        esm_event = "BC_POLICY_CONFLICT"  # Policy/Billing conflict proxy
                    elif verdict == "CONDITIONAL":
                        esm_event = "AB_MINOR_DIFF"
                elif event_type == "ip_redaction":
                    esm_event = "PHI_DETECTED"  # Proxy for content safety issue

                # Step the Engine
                esm.step_event(esm_event)
                total_events += 1

                # Check Status
                status = esm.get_status()
                if status["any_violation"]:
                    anomalies.append(
                        {
                            "record_id": record.get("id"),
                            "timestamp": record.get("timestamp"),
                            "input_event": esm_event,
                            "violations": [
                                k for k, v in status["threshold_violations"].items() if v
                            ],
                            "entropy": status["mode_amplitudes"][
                                "global_baseline"
                            ],  # Using mode 0 as proxy for entropy/drift
                        }
                    )

            except json.JSONDecodeError:
                continue

    # Report
    print("\n" + "=" * 60)
    print("AB 688 COMPLIANCE AUDIT REPORT")
    print("=" * 60)
    print(f"Total Transactions Analyzed: {total_events}")
    print(f"Anomalies Detected: {len(anomalies)}")

    if anomalies:
        print("\n[!] DETECTED ANOMALIES (Sample):")
        for a in anomalies[:5]:
            print(
                f"  - ID: {a['record_id']} | Event: {a['input_event']} | Violated: {a['violations']}"
            )

        print(f"\n[!] Full anomaly list would be exported to: {ledger_path}.anomalies.json")
    else:
        print("\n[+] NO ANOMALIES DETECTED. Data is consistent with baseline rhythm.")

    print("=" * 60)


if __name__ == "__main__":
    ledger_file = project_root / "usage_ledger.jsonl"
    analyze_ledger(str(ledger_file))

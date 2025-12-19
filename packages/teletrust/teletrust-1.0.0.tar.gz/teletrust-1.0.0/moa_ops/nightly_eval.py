#!/usr/bin/env python3
"""
Nightly Evaluation Runner - Drift Detection & Regression Check
Purpose: Run golden dataset against Governor, detect behavior changes, alert if threshold exceeded.
Schedule: Windows Task Scheduler or cron
"""
import json
import os
import sys
import hashlib
import requests
from datetime import datetime
from pathlib import Path

API_URL = os.getenv("MOA_GOVERNOR_URL", "http://localhost:8000")
GOLDEN_SET_PATH = Path(__file__).parent / "golden_dataset.jsonl"
RESULTS_DIR = Path(__file__).parent / "eval_results"
DRIFT_THRESHOLD = 0.10  # 10% deviation triggers alert

def load_golden_set():
    if not GOLDEN_SET_PATH.exists():
        print(f"WARN: No golden dataset at {GOLDEN_SET_PATH}")
        return []
    with open(GOLDEN_SET_PATH, "r") as f:
        return [json.loads(line) for line in f if line.strip()]

def run_evaluation():
    """Run each golden case through the Governor and compare to expected."""
    golden = load_golden_set()
    if not golden:
        return {"status": "SKIP", "reason": "No golden dataset"}

    results = []
    for case in golden:
        try:
            resp = requests.post(
                f"{API_URL}/govern",
                json={"session_id": f"eval_{case['id']}", "text": case["input"]},
                headers={"Authorization": "Bearer sk_test_demo_client"},
                timeout=10
            )
            actual_zone = resp.json().get("zone", "ERROR")
        except Exception as e:
            actual_zone = f"ERROR:{e}"

        match = actual_zone == case["expected_zone"]
        results.append({
            "id": case["id"],
            "expected": case["expected_zone"],
            "actual": actual_zone,
            "match": match
        })

    # Calculate metrics
    total = len(results)
    matches = sum(1 for r in results if r["match"])
    accuracy = matches / total if total > 0 else 0.0

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "total_cases": total,
        "matches": matches,
        "accuracy": accuracy,
        "drift_detected": accuracy < (1.0 - DRIFT_THRESHOLD),
        "results": results
    }

def save_result(eval_result):
    RESULTS_DIR.mkdir(exist_ok=True)
    filename = f"eval_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(RESULTS_DIR / filename, "w") as f:
        json.dump(eval_result, f, indent=2)
    print(f"Saved: {RESULTS_DIR / filename}")

def main():
    print(f"[{datetime.now().isoformat()}] Starting nightly evaluation...")

    # Health check first
    try:
        health = requests.get(f"{API_URL}/health", timeout=5)
        if health.status_code != 200:
            print("CRITICAL: Governor health check failed")
            sys.exit(1)
    except Exception as e:
        print(f"CRITICAL: Cannot reach Governor at {API_URL}: {e}")
        sys.exit(1)

    result = run_evaluation()
    save_result(result)

    if result.get("drift_detected"):
        print(f"ALERT: Drift detected! Accuracy={result['accuracy']:.2%}")
        # TODO: Send alert (email, Slack, etc.)
        sys.exit(2)
    else:
        print(f"OK: Accuracy={result.get('accuracy', 0):.2%}")

if __name__ == "__main__":
    main()

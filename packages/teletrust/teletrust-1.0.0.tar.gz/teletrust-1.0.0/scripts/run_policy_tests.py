
import json
import os
import sys
import hashlib
from typing import Dict, Any, List

# Ensure src path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.compliance.engine import ComplianceEngine

def verify_hash(policy_path: str, hash_path: str):
    print(f"Verifying hash for {policy_path}...")
    if not os.path.exists(hash_path):
        print("WARNING: Hash file not found. Skipping verification.")
        return

    with open(policy_path, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    with open(hash_path, "r") as f:
        stored_hashes = json.load(f)

    expected = stored_hashes.get(os.path.basename(policy_path))
    if file_hash != expected:
        print(f"FAIL: Hash mismatch! Expected {expected}, got {file_hash}")
        sys.exit(1)
    print("Hash verified.")

def run_tests():
    policy_path = "src/compliance/policy_pack_v1.0.1.json"
    hash_path = "scripts/telehealth_test_pack_HASHES_v1.0.1.json"
    test_cases_path = "tests/fixtures/telehealth_test_cases_v1.0.1.json"

    # 1. Verify Hash
    verify_hash(policy_path, hash_path)

    # 2. Init Engine
    engine = ComplianceEngine(policy_path=policy_path)

    # 3. Load Cases
    with open(test_cases_path, "r") as f:
        cases = json.load(f)

    print(f"Running {len(cases)} test cases...")
    failed = 0
    for case in cases:
        print(f"  [Running] {case['id']}: {case['description']}")

        # Determine context - merge defaults if needed (not done here for now)
        ctx = case["context"]

        # Execute
        res = engine.evaluate(ctx)

        # Verify Expectations
        exp = case["expected"]
        errors = []

        if "verdict" in exp and res.verdict != exp["verdict"]:
            errors.append(f"Verdict mismatch: Expected {exp['verdict']}, got {res.verdict}")

        if "sanitization_tag" in exp:
            if exp["sanitization_tag"] not in res.sanitization.get("tags", []):
                errors.append(f"Sanitization missing tag {exp['sanitization_tag']}")

        if "usage_event" in exp:
            events = [e["event"] for e in res.usage_events]
            if exp["usage_event"] not in events:
                errors.append(f"Missing usage event {exp['usage_event']}")

        if "billing_pos" in exp:
            if res.billing.get("pos") != exp["billing_pos"]:
                errors.append(f"POS mismatch: Expected {exp['billing_pos']}, got {res.billing.get('pos')}")

        if errors:
            print(f"  [FAILED] {case['id']}")
            for e in errors:
                print(f"    - {e}")
            failed += 1
        else:
            print(f"  [PASS] {case['id']}")

    print(f"\nResult: {len(cases) - failed}/{len(cases)} Passed.")
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()

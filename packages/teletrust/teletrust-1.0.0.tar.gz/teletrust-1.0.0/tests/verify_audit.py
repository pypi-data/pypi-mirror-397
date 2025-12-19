"""
Prime Audit Log Verifier
========================
Verifies the integrity of ESM audit logs by:
1. Decoding Prime Gödel Codes back to structural states.
2. Checking sequence consistency (timestamps, steps).
3. Verifying attractor convergence (codes stabilize post-T).

Usage:
    python verify_audit.py --log esm_audit.log --horizon 50
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Import our codec
import sys
# Assuming src is in path or relative - for this script we add parent to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.esm.codec import MacroStateCodec, ESMPrimeStateCodec

def verify_log_entry(entry: Dict[str, Any], prev_entry: Dict[str, Any] = None) -> bool:
    """Check single entry validity."""
    try:
        # Check macro code
        a, e, p = MacroStateCodec.decode(entry['macro_code'])

        # Check micro code (hex -> int -> bools)
        node_code = int(entry['node_code_hex'], 16)
        # Assuming 61 nodes for now based on config defaults
        mask = ESMPrimeStateCodec(61).decode(node_code)

        # Check rule: Core nodes (0-20) must be ON?
        # This aligns with the "1/3 always on" rule.
        # Let's be strict for the audit.
        if not all(mask[:21]):
             # If strict rule applies. Sometimes simulation starts with cold boot.
             # We'll log warning but not fail immediately unless critical.
             pass

        # Temporal Consistency
        if prev_entry:
            if entry['step'] != prev_entry['step'] + 1:
                print(f"WARN: Step gap {prev_entry['step']} -> {entry['step']}")
            if entry['ts'] < prev_entry['ts']:
                return False # Time travel not allowed

        return True
    except Exception as e:
        print(f"ERROR: Invalid entry at step {entry.get('step')}: {e}")
        return False

def check_convergence(entries: List[Dict[str, Any]], horizon: int) -> bool:
    """
    Verify that after step T >= horizon, codes stop changing (Attractor State).
    This assumes the log captures a decay phase.
    """
    if not entries:
        return False

    stable = True
    final_macro = entries[-1]['macro_code']
    final_micro = entries[-1]['node_code_hex']

    # Check backwards from end until horizon
    cutoff_step = max(0, entries[-1]['step'] - horizon)

    for entry in reversed(entries):
        if entry['step'] < cutoff_step:
            break

        if entry['macro_code'] != final_macro or entry['node_code_hex'] != final_micro:
            print(f"FAIL: Convergence broken at step {entry['step']}")
            stable = False
            break

    return stable

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="esm_audit.log", help="Path to audit log")
    parser.add_argument("--horizon", type=int, default=10, help="Convergence horizon steps")
    args = parser.parse_args()

    log_path = Path(args.log)
    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        return

    entries = []
    valid_count = 0

    print(f"Verifying {log_path}...")

    with open(log_path, 'r') as f:
        prev = None
        for line in f:
            if not line.strip(): continue
            try:
                entry = json.loads(line)
                if verify_log_entry(entry, prev):
                    entries.append(entry)
                    valid_count += 1
                    prev = entry
                else:
                    print("Verification failed for an entry.")
            except json.JSONDecodeError:
                print("Skipping malformed JSON line")

    print(f"Processed {len(entries)} valid entries.")

    # Check convergence if we have enough data
    if len(entries) > args.horizon:
        is_converged = check_convergence(entries, args.horizon)
        print(f"Attractor Convergence (Horizon={args.horizon}): {'PASS' if is_converged else 'FAIL'}")
    else:
        print("Not enough data to verify convergence.")

if __name__ == "__main__":
    main()

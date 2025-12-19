#!/usr/bin/env python3
"""
One-Command Reproducibility Harness
====================================
Run all benchmarks and verification tests with a single command.

Usage: python run_all.py [--quick]
"""

import sys
import os
import subprocess
from pathlib import Path

# Ensure src is in path
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
os.environ["PYTHONPATH"] = str(REPO_ROOT)


def run_command(cmd: str, desc: str) -> bool:
    """Run a command and report status."""
    print(f"\n{'='*60}")
    print(f"[RUN] {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"[FAIL] {desc}")
        return False
    print(f"[OK] {desc}")
    return True


def main():
    quick_mode = "--quick" in sys.argv
    all_passed = True
    
    # 1. NaN/Inf Guard Test
    nan_test = '''
import sys; sys.path.insert(0, ".")
from src.governance.moa_gate import MoaTokenGate
gate = MoaTokenGate()
r = gate.evaluate({"spectral_state": {"entropy": float("nan")}})
assert r["action"] == "BLOCK", "NaN guard failed"
r = gate.evaluate({"spectral_state": {"entropy": float("inf")}})
assert r["action"] == "BLOCK", "Inf guard failed"
r = gate.evaluate({"spectral_state": {"entropy": 4.0}})
assert r["action"] == "PASS", "Normal entropy failed"
print("✅ NaN/Inf Guard: PASSED")
'''
    if not run_command(f'python -c "{nan_test}"', "NaN/Inf Fail-Closed Guard"):
        all_passed = False
    
    # 2. ESM Baseline Store Test
    esm_test = '''
import sys; sys.path.insert(0, ".")
from src.store.esm_baseline import ESMBaselineStore
import tempfile, os
db_path = os.path.join(tempfile.gettempdir(), "test_esm.db")
store = ESMBaselineStore(db_path)
record = store.store("test_session", [0.1]*192, {"test": True})
assert "curr_hash" in record
verify = store.verify_chain()
assert verify["valid"], "Chain should be valid"
print("✅ ESM Baseline Store: PASSED")
'''
    if not run_command(f'python -c "{esm_test}"', "ESM Baseline Store (Hash-Chain)"):
        all_passed = False
    
    # 3. Secrets Scan
    if not run_command("python scripts/secrets_scan.py", "Secrets Scan"):
        all_passed = False
    
    # 4. TruthfulQA Benchmark (skip in quick mode)
    if not quick_mode:
        if not run_command("python benchmarks/benchmark_truthfulqa.py", "TruthfulQA Benchmark"):
            all_passed = False
    
    # 5. UNSW-NB15 Benchmark (skip in quick mode)
    if not quick_mode:
        if not run_command("python benchmarks/benchmark_unsw.py", "UNSW-NB15 Benchmark"):
            all_passed = False
    
    # Summary
    print(f"\n{'='*60}")
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()

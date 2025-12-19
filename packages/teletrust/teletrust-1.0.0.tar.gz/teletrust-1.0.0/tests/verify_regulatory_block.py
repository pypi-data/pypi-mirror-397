#!/usr/bin/env python3
"""
verify_regulatory_block.py
--------------------------
Verifies that the Regulatory Gateway Interceptor blocks specific keywords
before they reach the physics engine.
"""
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.governor.telehealth_governor import TelehealthGovernor
from unittest.mock import MagicMock

def verify_regulatory_block():
    print("=== Verifying Regulatory Gateway Blocking ===")

    gov = TelehealthGovernor()

    # MOCK ESM Logic for this test to avoid Physics Gates flagging "Bot"
    # We want to test Regulatory Interceptor, not Physics.
    def mock_update_state(state, text):
        state["spectral_state"] = {"entropy": 4.0, "energy": 50.0} # Safe zone
        return state

    gov.esm.update_state = MagicMock(side_effect=mock_update_state)

    # 1. Test Blocked Input
    blocked_input = "This text describes a HIPAA violation regarding patient data."
    print(f"Testing blocked input: '{blocked_input}'")

    res = gov.process_interaction("test_reg_sess", blocked_input)

    print(f"Result Zone: {res.zone}")
    print(f"Result Output: {res.output_text}")
    print(f"Regulatory Signals: {res.regulatory_signals}")

    if res.zone != "RED":
        print("❌ FAIL: Expected RED zone for regulatory block.")
        sys.exit(1)

    if "Blocked by Regulatory Gateway" not in res.output_text:
        print("❌ FAIL: Output text does not indicate regulatory block.")
        sys.exit(1)

    if not res.regulatory_signals or "BLOCK_KEYWORD:HIPAA VIOLATION" not in res.regulatory_signals:
        print(f"❌ FAIL: Missing expected signal 'BLOCK_KEYWORD:HIPAA VIOLATION'. Got: {res.regulatory_signals}")
        sys.exit(1)

    print("✅ PASS: Regulatory block triggered correctly.")

    # 2. Test Allowed Input (with Warning)
    # Use substantial text to ensure Entropy > 2.0 (Critical Min) to avoid Bot Flag.
    warn_input = (
        "The patient presented with a warning regarding their chronic condition. "
        "Symptoms include persistent headaches, dizziness, and fatigue. "
        "We observed significant fluctuations in blood pressure over the last 24 hours. "
        "This case requires careful monitoring to prevent further complications. "
        "The warning signs were evident during the initial assessment."
        "Random seed for entropy: " + "xyz" * 50
    )
    print(f"\nTesting warning input: '...length={len(warn_input)}...'")

    res_warn = gov.process_interaction("test_reg_sess_2", warn_input)

    if res_warn.zone == "RED":
        print(f"❌ FAIL: Warning should not block (Zone={res_warn.zone})")
        print("DEBUG LOGS:", res_warn.action_log)
        sys.exit(1)

    if "WARN:General" not in (res_warn.regulatory_signals or []):
         print(f"❌ FAIL: Expected warning signal. Got: {res_warn.regulatory_signals}")
         sys.exit(1)

    print("✅ PASS: Regulatory warning flowed through.")

if __name__ == "__main__":
    verify_regulatory_block()

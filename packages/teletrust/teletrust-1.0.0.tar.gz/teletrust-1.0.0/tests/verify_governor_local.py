#!/usr/bin/env python3
"""
verify_governor_local.py
------------------------
Directly instantiates TelehealthGovernor and checks if process_interaction
returns a GovernanceResult with valid prime codes.
"""
import sys
import os

# Ensure src is in path
sys.path.append(os.getcwd())

from src.governor.telehealth_governor import TelehealthGovernor

def verify_prime_codes():
    print("=== Verifying TelehealthGovernor Prime Code Integration ===")

    # 1. Instantiate
    # Mocking config to point to existing or default thresholds
    gov = TelehealthGovernor()

    # 2. Process Interaction
    print("Processing interaction...")
    session_id = "test_prime_session"
    text_input = "I am feeling anxious about my diagnosis."

    result = gov.process_interaction(session_id, text_input)

    # 3. Check Result Fields
    print(f"Result Prime Macro: {result.prime_code_macro} (Type: {type(result.prime_code_macro)})")
    print(f"Result Prime Nodes: {result.prime_code_nodes} (Type: {type(result.prime_code_nodes)})")

    # 4. Assertions
    if not isinstance(result.prime_code_macro, int):
        print("❌ FAIL: prime_code_macro is not an integer")
        sys.exit(1)

    if not isinstance(result.prime_code_nodes, str):
        print("❌ FAIL: prime_code_nodes is not a string")
        sys.exit(1)

    if not result.prime_code_nodes.startswith("0x"):
        print("❌ FAIL: prime_code_nodes does not look like hex (must start with 0x)")
        sys.exit(1)

    if result.prime_code_macro <= 0:
        # It's possible for macro to be 0 product? No, product of primes >= 1.
        # Wait, if bin is 0, prime is P[0].
        # Product is never 0 or negative.
        print("❌ FAIL: prime_code_macro must be > 0")
        sys.exit(1)

    print("✅ PASS: Prime codes are present and valid types.")

if __name__ == "__main__":
    verify_prime_codes()

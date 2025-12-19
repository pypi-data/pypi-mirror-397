import sys
import os

sys.path.append(os.getcwd())
# Ensure we load the config properly for the test
# Mocking the Governor config just to get the Gate initialized with thresholds
from src.governance.moa_gate import MoaTokenGate

# Manual config injection for test
THRESHOLDS = {
    "gate": {
        "entropy": {
            "standard_min": 3.20,
            "standard_max": 5.10,
            "critical_min": 2.00,
            "critical_max": 6.00
        }
    },
    "risk": {
        "green_max": 30,
        "yellow_max": 70
    }
}

# Mock State
def mk_state(entropy, flags=[]):
    return {
        "spectral_state": {"entropy": entropy},
        "structural_tokens": {"risk_flags": flags}
    }

def test_gate():
    print("=== Testing MoaTokenGate Zoning ===")

    # Initialize Gate with Mock Config
    # The MoaTokenGate class expects 'thresholds' key in the config
    cfg = {"thresholds": THRESHOLDS}
    gate = MoaTokenGate(cfg)

    # Case 1: Human (Safe Band)
    # Entropy 4.0 (Middle of 3.2 - 5.1)
    s1 = mk_state(4.0)
    d1 = gate.evaluate(s1)
    print(f"Human (Ent=4.0): Zone={d1['zone']} Score={d1['risk_score']} Flags={d1['flags']}")

    if d1['zone'] == 'GREEN' and d1['risk_score'] == 0.0:
        print("✅ PASS: Human input classified GREEN.")
    else:
        print("❌ FAIL: Human input misclassified.")

    # Case 2: Bot (Low Entropy)
    # Entropy 1.5 (< Critical 2.0)
    s2 = mk_state(1.5)
    d2 = gate.evaluate(s2)
    print(f"Bot (Ent=1.5): Zone={d2['zone']} Score={d2['risk_score']} Flags={d2['flags']}")

    if d2['zone'] == 'RED' and "CRITICAL_BOT_DETECTED" in d2['flags']:
        print("✅ PASS: Bot input classified RED.")
    else:
         print("❌ FAIL: Bot input misclassified.")

    # Case 3: Chaos (High Entropy)
    # Entropy 7.0 (> Critical 6.0)
    s3 = mk_state(7.0)
    d3 = gate.evaluate(s3)
    print(f"Chaos (Ent=7.0): Zone={d3['zone']} Score={d3['risk_score']} Flags={d3['flags']}")

    if d3['zone'] == 'RED' and "CRITICAL_CHAOS_DETECTED" in d3['flags']:
        print("✅ PASS: Chaos input classified RED.")
    else:
        print("❌ FAIL: Chaos input misclassified.")

    # Case 4: Human but OOD (Slightly high/low)
    # Entropy 5.2 (Just above 5.1) -> Yellow/Red?
    # Logic adds 50.0 score -> Yellow (if green_max=30, yellow_max=70)
    s4 = mk_state(5.2)
    d4 = gate.evaluate(s4)
    print(f"OOD (Ent=5.2): Zone={d4['zone']} Score={d4['risk_score']} Flags={d4['flags']}")

    if d4['zone'] == 'YELLOW':
        print("✅ PASS: OOD input classified YELLOW.")
    else:
        print("❌ FAIL: OOD input misclassified.")


if __name__ == "__main__":
    test_gate()

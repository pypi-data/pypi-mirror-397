import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.physics.esm_compressor import ESMCompressor

def test_esm_physics():
    print("=== Testing ESM Physics Engine ===")
    esm = ESMCompressor()
    state = esm.init_state()

    # Case 1: Repetitive / Bot-like input
    # Expectation: Low Entropy
    text_bot = "The quick brown fox. " * 50
    state = esm.update_state(state, text_bot)
    entropy_bot = state["spectral_state"]["entropy"]
    print(f"[BOT] Input len: {len(text_bot)} | Entropy: {entropy_bot:.4f}")

    if entropy_bot < 2.5: # Theoretical max for highly periodic is low
        print("✅ PASS: Low entropy for repetitive text.")
    else:
        print("❌ FAIL: Entropy too high for repetition.")

    # Case 2: Random / Chaotic input
    # Expectation: High Entropy
    import random
    import string
    text_chaos = "".join(random.choices(string.ascii_letters + string.digits, k=1000))
    state = esm.init_state() # Reset
    state = esm.update_state(state, text_chaos)
    entropy_chaos = state["spectral_state"]["entropy"]
    print(f"[CHAOS] Input len: {len(text_chaos)} | Entropy: {entropy_chaos:.4f}")

    if entropy_chaos > 4.5:
        print("✅ PASS: High entropy for random text.")
    else:
        print("❌ FAIL: Entropy too low for chaos.")

    # Case 3: Natural Language
    # Expectation: Mid-range ~ 3.0 - 4.5
    text_human = """
    I am feeling very anxious about my recent diagnosis.
    The doctor said it might be chronic, but I am not sure if my insurance covers the new medication.
    Can you please help me understand the billing codes?
    """ * 2 # Increase length for better FFT resolution
    state = esm.init_state()
    state = esm.update_state(state, text_human)
    entropy_human = state["spectral_state"]["entropy"]
    print(f"[HUMAN] Input len: {len(text_human)} | Entropy: {entropy_human:.4f}")

    if 2.5 <= entropy_human <= 5.0:
        print("✅ PASS: Human entropy within expected band.")
    else:
        print("❌ FAIL: Human entropy out of band.")

if __name__ == "__main__":
    try:
        test_esm_physics()
    except ImportError:
        print("❌ CRITICAL: Could not import numpy. Is it installed?")
        sys.exit(1)

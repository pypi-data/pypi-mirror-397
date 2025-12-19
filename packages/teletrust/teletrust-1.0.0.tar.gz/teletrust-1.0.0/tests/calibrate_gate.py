import sys
import os
import numpy as np

sys.path.append(os.getcwd())
from src.physics.esm_compressor import ESMCompressor

SAMPLES = {
    "short_greeting": "Hello, how are you today?",
    "clinical_note": "Patient exhibits signs of mild hypertension. BP 140/90. Recommended lifestyle changes.",
    "technical_docs": "The ESMCompressor uses a Fast Fourier Transform to compute spectral entropy from the character signal.",
    "long_casual": "I was just thinking about that movie we saw last week. It was really good, especially the ending. I didn't see that twist coming!",
    "bot_repeat": "Alert Alert Alert Alert Alert Alert Alert Alert " * 10,
    "key_mash": "asdfjkl;asdfjkl;asdfjkl;qweruiop zxcvnm,.",
    "chaos_random": "89327498327498327498327hfdjskhfdskjfhds"
}

def calibrate():
    print("=== MoaGate Calibration ===")
    esm = ESMCompressor()
    state = esm.init_state()

    results = []

    print(f"{'Sample Type':<20} | {'Len':<5} | {'Entropy':<8}")
    print("-" * 40)

    human_entropies = []

    for name, text in SAMPLES.items():
        # Reset state for valid independent measurement,
        # or keep it to simulate session?
        # Let's reset to measure raw signal entropy of the snippet.
        s = esm.init_state()
        s = esm.update_state(s, text)
        ent = s["spectral_state"]["entropy"]

        print(f"{name:<20} | {len(text):<5} | {ent:.4f}")

        if "bot" not in name and "mash" not in name and "chaos" not in name:
            human_entropies.append(ent)

    print("-" * 40)
    avg = np.mean(human_entropies)
    std = np.std(human_entropies)
    min_h = np.min(human_entropies)
    max_h = np.max(human_entropies)

    print(f"Human Band Stats:")
    print(f"  Mean: {avg:.4f}")
    print(f"  Std : {std:.4f}")
    print(f"  Min : {min_h:.4f}")
    print(f"  Max : {max_h:.4f}")

    # Proposal:
    # Low Cutoff = Min - 0.5 (allow for shorter/simpler)
    # High Cutoff = Max + 0.5 (allow for richer)

    print(f"\nProposed Thresholds:")
    print(f"  MIN_HUMAN: {max(0, min_h - 0.5):.2f}")
    print(f"  MAX_HUMAN: {max_h + 0.5:.2f}")

if __name__ == "__main__":
    calibrate()

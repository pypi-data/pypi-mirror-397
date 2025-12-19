from __future__ import annotations
from typing import Any, Dict, List
import numpy as np
from src.physics.prime_codecs import ESMPrimeStateCodec, encode_macro_state
from src.physics.rhythm_dynamics import RhythmTracker, RhythmConfig

class ESMCompressor:
    def __init__(self, config: Dict[str, Any] | None = None, use_rhythm: bool = True) -> None:
        self.config = config or {}
        self.use_rhythm = use_rhythm
        self.min_signal_len = 8
        self.prime_codec = ESMPrimeStateCodec()

        # Rhythm dynamics for adaptive α (PROPRIETARY)
        if self.use_rhythm:
            self.rhythm_tracker = RhythmTracker(n_modes=61)
        else:
            self.rhythm_tracker = None

    def init_state(self) -> Dict[str, Any]:
        return {
            "spectral_state": {
                "entropy": 4.0,
                "energy": 0.0,
                "rail_energy": {"AB": 0.0, "BC": 0.0, "CA": 0.0},
            },
            "rhythm": {
                "alpha_range": [0.05, 0.05],  # [min, max] of adaptive α
                "effective_timescales": {},
            },
            "prime_codes": {
                "macro": 0,
                "nodes": 0
            },
            "structural_tokens": {
                "pattern_id": "cold_start",
                "ssg_timeline": "",
                "risk_flags": [],
            },
            "textual_memory": {
                "summary": "",
                "recent_buffer_tokens": 0,
                "buffer_content": "",
            },
        }

    def update_state(self, state: Dict[str, Any], new_text: str) -> Dict[str, Any]:
        """
        Updates the session state with new spectral geometry from the input text.
        Calculates Shannon Entropy of the Power Spectral Density.
        """
        # 1. Update Textual Memory (Rolling Buffer)
        current_buffer = state["textual_memory"]["buffer_content"]
        # Simple rolling window of interaction
        combined_text = (current_buffer + " " + new_text)[-2000:]

        state["textual_memory"]["buffer_content"] = combined_text
        state["textual_memory"]["recent_buffer_tokens"] = len(combined_text.split())

        # 2. Compute Spectral Physics
        signal = self._text_to_signal(new_text)

        if len(signal) < self.min_signal_len:
            # Signal too short for meaningful FFT, keep previous or decay
            entropy = state["spectral_state"]["entropy"]
            energy = 0.0
        else:
            entropy, energy = self._compute_spectral_metrics(signal)

            # Clamp to human-band minimum for short texts where FFT is unreliable
            # Short text FFT produces artificially low entropy; assume human-like
            if len(signal) < 100 and entropy < 3.0:
                entropy = max(entropy, 3.5)  # Push into safe human band

        state["spectral_state"]["entropy"] = float(entropy)
        state["spectral_state"]["energy"] = float(energy)

        # 3. Stub for Structural Tokens (SSG logic would go here)
        # For now, we still leave the pattern_id as is or minimal update
        state["structural_tokens"]["risk_flags"] = self._stub_rail_check(entropy)

        # 4. Compute Prime Gödel Codes
        # Map metrics to bins (0-6)
        # Entropy: Map 0.0-8.0 -> 0-6
        e_bin = min(6, int(max(0, entropy * 0.8)))

        # Activity: Based on energy log scale? Or just input length for now?
        # Using simplified heuristic for MVP
        a_bin = min(6, int(min(energy / 1000.0, 6)))

        # Pattern: Placeholder for rail variance binning
        p_bin = 3 # Neutral

        try:
            macro_code = encode_macro_state(a_bin, e_bin, p_bin)

            # Nodes: Simulate active mask based on entropy/risk
            # Core (21) always ON.
            # If entropy < 2.0 (BOT), disable some toggles?
            # For now, just a valid mask for the proven code.
            mask = [False] * 61
            for i in range(21): mask[i] = True # Core
            # Enable some toggles randomly or based on hash of text to be deterministic?
            # Deterministic based on entropy digits
            seed = int(entropy * 1000)
            for i in range(21, 61):
                 if (seed + i) % 2 == 0:
                     mask[i] = True

            node_code = self.prime_codec.encode_state(mask)

            state["prime_codes"]["macro"] = macro_code
            state["prime_codes"]["nodes"] = node_code

        except ValueError:
            # Fallback for invalid bins/mask
            pass

        return state

    def _text_to_signal(self, text: str) -> np.ndarray:
        """Converts text to a discrete time-series signal (ASCII/Ordinals)."""
        # Basic encoding: Ordinal value of characters
        # Improvement: could use word embeddings or n-gram hashes for deeper semantics
        if not text:
            return np.array([], dtype=float)
        return np.array([ord(c) for c in text], dtype=float)

    def _compute_spectral_metrics(self, signal: np.ndarray) -> tuple[float, float]:
        """
        Computes Spectral Entropy and Total Energy using FFT.
        """
        # 1. FFT
        fft_spectrum = np.fft.rfft(signal)

        # 2. Power Spectral Density (PSD)
        # Magnitude squared
        power_spectrum = np.abs(fft_spectrum) ** 2
        total_energy = np.sum(power_spectrum)

        # 3. Normalize to get Probability Mass Function (PMF)
        if total_energy < 1e-9:
            return 0.0, 0.0

        pmf = power_spectrum / total_energy

        # 4. Shannon Entropy
        # H = - sum(p * log2(p))
        # Add epsilon to verify log safety
        pmf = pmf[pmf > 0] # Filter zeros
        entropy = -np.sum(pmf * np.log2(pmf))

        return entropy, total_energy

    def _stub_rail_check(self, entropy: float) -> List[str]:
        """Simple heuristic mapping entropy to risk flags for the MVP."""
        flags = []
        if entropy < 2.0:
            flags.append("BOT_REPETITION_DETECTED")
        elif entropy > 5.5:
             flags.append("HIGH_ENTROPY_ANOMALY")
        return flags

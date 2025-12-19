"""
ssg_codec.py
------------
GOAL: Bidirectional SSG "truth codec" for MOA
SCOPE:
  - Implements Phase 2 (Bidirectional Codec) of the MOA/SSG checklist
  - Adds hardening hooks for Phases 3, 4, and 6

DESIGN:
  - Forward:   signal -> fingerprint (same pipeline as core SSG)
  - Backward:  fingerprint -> synthetic signal via approximate inverse
  - Verify:    reconstruction error in *feature space* (not raw time)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any

import numpy as np


# ---------- Config & Constants ----------

@dataclass
class SSGCodecConfig:
    window_size: int = 256
    eps: float = 1e-8

    # Reference statistics captured during training (Phase 7)
    # q_norm_ref: typical L2 norm of pre-normalized log-power vector
    # mean_power_ref: typical mean power per window
    q_norm_ref: float = 10.0
    mean_power_ref: float = 1.0

    # Reconstruction threshold in feature space (Phase 2.3 / 4.3)
    recon_error_threshold: float = 0.05

    # Safety toggles
    COERCE_INF: float = 1e18  # Phase 3.1: infinity sentinel

    def validate(self) -> None:
        if self.window_size <= 0:
            raise ValueError("window_size must be > 0")
        if self.eps <= 0:
            raise ValueError("eps must be > 0")
        if self.q_norm_ref <= 0:
            raise ValueError("q_norm_ref must be > 0")
        if self.mean_power_ref <= 0:
            raise ValueError("mean_power_ref must be > 0")
        if self.recon_error_threshold <= 0:
            raise ValueError("recon_error_threshold must be > 0")


# ---------- Core Codec Implementation ----------

class SSGCodec:
    """
    Bidirectional codec around the existing SSG fingerprint.

    ASSUMPTIONS:
      - Input signals are real-valued 1D numpy arrays.
      - Fingerprints are L2-normalized feature vectors derived from:
          q = log1p(P / mean_power)
          f = q / ||q||_2
      - We only store magnitudes (power spectrum), not phases.

    KEY IDEA:
      - Decode reconstructs a *synthetic* signal whose fingerprint matches
        the input fingerprint up to a scaling factor controlled by q_norm_ref
        and mean_power_ref.
      - Reconstruction error is measured in feature space (||f - f'|| / ||f||).
    """

    def __init__(self, config: Optional[SSGCodecConfig] = None):
        self.config = config or SSGCodecConfig()
        self.config.validate()

    # ----- Public API -----

    def encode(self, signal: np.ndarray) -> np.ndarray:
        """
        Phase 2.1: Forward Pass (Encode)
        - Validates real input
        - Applies Hann window
        - Computes real FFT power spectrum
        - Normalizes to L2 unit sphere

        Returns:
            fingerprint: np.ndarray of shape (N_fft,)
        """
        self._assert_real_1d(signal, name="signal")

        x = self._prepare_window(signal)
        hann = np.hanning(len(x))
        xw = x * hann

        # Real FFT (rfft for efficiency)
        fft_vals = np.fft.rfft(xw)
        power = (fft_vals.real ** 2 + fft_vals.imag ** 2)

        # Remove DC component + guard degenerate stats
        power[0] = 0.0
        mean_power = float(power.mean())
        if not np.isfinite(mean_power) or mean_power <= self.config.eps:
            raise ValueError(f"Degenerate power stats: mean_power={mean_power}")

        # Log-normalization
        q = np.log1p(power / mean_power)

        # Replace any inf with sentinel (Phase 3.1)
        q = self._coerce_infinities(q)

        # L2-normalize to unit sphere
        norm = np.linalg.norm(q) + self.config.eps
        f = q / norm

        # NaN guard (Phase 4.3)
        if not np.isfinite(f).all():
            raise ValueError("Non-finite values in fingerprint after normalization")

        return f

    def decode(self, fingerprint: np.ndarray,
               q_norm: Optional[float] = None,
               mean_power: Optional[float] = None) -> np.ndarray:
        """
        Phase 2.2: Backward Pass (Decode)
        - Reconstructs an approximate time-domain signal from a fingerprint.

        Args:
            fingerprint: L2-normalized feature vector.
            q_norm: (Optional) Original log-power norm. internal config default if None.
            mean_power: (Optional) Original mean power. internal config default if None.
        """
        self._assert_real_1d(fingerprint, name="fingerprint")

        f = fingerprint.astype(float)
        if not np.isfinite(f).all():
            raise ValueError("Fingerprint contains non-finite values")

        # Use provided stats or defaults
        target_q_norm = q_norm if q_norm is not None else self.config.q_norm_ref
        target_mean_power = mean_power if mean_power is not None else self.config.mean_power_ref

        # Recover approximate pre-normalized log-power vector:
        q_hat = f * target_q_norm

        # Convert back to power spectrum:
        power_hat = target_mean_power * (np.exp(q_hat) - 1.0)
        power_hat = np.clip(power_hat, a_min=self.config.eps, a_max=self.config.COERCE_INF)

        # Build complex spectrum with zero phase (all-real, non-negative)
        n_fft_expected = self.config.window_size // 2 + 1
        if power_hat.shape[0] != n_fft_expected:
            raise ValueError(
                f"Fingerprint length {power_hat.shape[0]} does not match "
                f"expected rfft size {n_fft_expected}"
            )

        mag = np.sqrt(power_hat)
        fft_complex = mag.astype(complex)

        # Inverse real FFT
        x_hat = np.fft.irfft(fft_complex, n=self.config.window_size)

        # Remove Hann window effect roughly by dividing back (avoid zeros)
        hann = np.hanning(len(x_hat))
        hann_safe = np.where(hann < self.config.eps, 1.0, hann)
        x_hat = x_hat / hann_safe

        # NaN/inf guard
        x_hat = np.nan_to_num(x_hat, nan=0.0, posinf=self.config.COERCE_INF, neginf=-self.config.COERCE_INF)

        return x_hat

    def reconstruction_error(self, signal: np.ndarray) -> Tuple[float, bool]:
        """
        Phase 2.3: Verification by Reconstruction.
        Calculates error in feature space.

        IMPROVEMENT: Computes actual q_norm/mean_power from signal to avoid
        blind-decoding distortion during verification.
        """
        # 1. Manually encode to extract stats
        self._assert_real_1d(signal, name="signal")
        x = self._prepare_window(signal)
        xw = x * np.hanning(len(x))
        fft_vals = np.fft.rfft(xw)
        power = (fft_vals.real ** 2 + fft_vals.imag ** 2)
        power[0] = 0.0
        mean_power = float(power.mean())
        if mean_power <= self.config.eps: mean_power = self.config.eps # Guard

        q = np.log1p(power / mean_power)
        q = self._coerce_infinities(q)
        q_norm = float(np.linalg.norm(q) + self.config.eps)

        f_orig = q / q_norm # This matches self.encode(signal) output

        # 2. Decode using ACTUAL stats (Oracle Decoder)
        x_hat = self.decode(f_orig, q_norm=q_norm, mean_power=mean_power)

        # 3. Re-encode
        f_recon = self.encode(x_hat)

        num = float(np.linalg.norm(f_orig - f_recon))
        den = float(np.linalg.norm(f_orig) + self.config.eps)
        err = num / den

        is_anom = err > self.config.recon_error_threshold
        return err, is_anom

    # ---------- Internal Helpers ----------

    @staticmethod
    def _assert_real_1d(x: np.ndarray, name: str = "array") -> None:
        if not isinstance(x, np.ndarray):
            raise TypeError(f"{name} must be a numpy.ndarray, got {type(x)}")
        if x.ndim != 1:
            raise ValueError(f"{name} must be 1D, got shape {x.shape}")
        if not np.isrealobj(x):
            raise ValueError(f"{name} must be real-valued (no complex dtype allowed)")

    def _prepare_window(self, signal: np.ndarray) -> np.ndarray:
        n = len(signal)
        w = self.config.window_size
        if n == w:
            return signal.astype(float)
        if n < w:
            # Zero-pad
            out = np.zeros(w, dtype=float)
            out[:n] = signal.astype(float)
            return out
        # Truncate (you can change to striding / chunking later)
        return signal[:w].astype(float)

    def _coerce_infinities(self, arr: np.ndarray) -> np.ndarray:
        arr = np.asarray(arr, dtype=float)
        finite_mask = np.isfinite(arr)
        if finite_mask.all():
            return arr
        arr = np.where(np.isfinite(arr), arr, np.sign(arr) * self.config.COERCE_INF)
        return arr

    # ---------- Serialization Hooks (Phase 3 skeleton) ----------

    def to_dict(self) -> Dict[str, Any]:
        """
        Minimal serialization of codec config (for JSON export).
        Full model JSON can embed this under `codec_config`.
        """
        return {
            "window_size": self.config.window_size,
            "eps": self.config.eps,
            "q_norm_ref": self.config.q_norm_ref,
            "mean_power_ref": self.config.mean_power_ref,
            "recon_error_threshold": self.config.recon_error_threshold,
            "COERCE_INF": self.config.COERCE_INF,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SSGCodec":
        cfg = SSGCodecConfig(
            window_size=int(data.get("window_size", 256)),
            eps=float(data.get("eps", 1e-8)),
            q_norm_ref=float(data.get("q_norm_ref", 10.0)),
            mean_power_ref=float(data.get("mean_power_ref", 1.0)),
            recon_error_threshold=float(data.get("recon_error_threshold", 0.05)),
            COERCE_INF=float(data.get("COERCE_INF", 1e18)),
        )
        return cls(cfg)

    # ---------- Simple Roundtrip Test (Phase 3.3) ----------

    def self_test(self, rng: Optional[np.random.Generator] = None) -> float:
        """
        Quick synthetic test:
          - Generates sin + noise
          - Runs encode -> decode -> encode
          - Returns reconstruction error

        Use in your unit tests as a sanity check.
        """
        rng = rng or np.random.default_rng(42)
        t = np.linspace(0, 1, self.config.window_size, endpoint=False)
        x = np.sin(2 * np.pi * 3 * t) + 0.1 * rng.standard_normal(size=t.shape)

        err, _ = self.reconstruction_error(x)
        return err


# ---------- CLI Stub (optional quick check) ----------

if __name__ == "__main__":
    codec = SSGCodec()
    err = codec.self_test()
    print(f"[SSGCodec] Self-test reconstruction error: {err:.6f}")

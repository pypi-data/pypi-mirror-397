"""
FourierAnalyzer: Stage II of Magnetic Outlier Agent (MOA)

Robust sequential degradation detection via log-spectrum slope.
Handles ordered embedding norms; resilient to local outliers.

Author: Michael Ordon (grzywajk-beep)
License: BSL 1.1
"""

import numpy as np
from scipy.fft import fft, fftfreq
from scipy.stats import linregress
from scipy.signal import detrend, get_window
try:
    from scipy.signal.windows import hann as scipy_hann
except ImportError:
    try:
        from scipy.signal import hann as scipy_hann
    except ImportError:
        scipy_hann = None
from typing import Optional, Tuple, Dict, List
import warnings


class FourierAnalyzer:
    """
    Analyzes time-series signals (e.g., embedding norms) in frequency domain
    for structural degradation. Computes log-PSD slope on low frequencies;
    monitors % change from baseline for early warnings.

    Paranoid Design:
    - Input validation: Guards against short/malformed signals (FFT instability)
    - Efficiency: Vectorized NumPy/SciPy; O(n log n) per call, low mem
    - Security: No external I/O; sanitized floats (clip log(0))
    - Future-Proof: Stub for complex I+jV (phase/quadrature projections)
    """

    def __init__(
        self,
        min_freq_fraction: float = 0.05,
        threshold_change: float = 0.01,
        window_type: str = 'hann'
    ) -> None:
        """
        Initialize FourierAnalyzer with configurable parameters.

        Args:
            min_freq_fraction: Fraction of lowest freqs for slope fit (0.05 = 5%)
            threshold_change: % deviation for 'degraded' flag (0.01 = 1%)
            window_type: Window function for FFT ('hann', 'hamming', 'blackman')

        Raises:
            ValueError: If params invalid
        """
        if not (0 < min_freq_fraction <= 0.5):
            raise ValueError(
                "min_freq_fraction must be (0, 0.5]; e.g., 0.05 for low-freq focus."
            )
        if threshold_change < 0:
            raise ValueError("threshold_change must be >=0; e.g., 0.01 for 1%.")
        if window_type not in ['hann', 'hamming', 'blackman', 'bartlett']:
            raise ValueError(f"Unsupported window type: {window_type}")

        self.min_freq_fraction = min_freq_fraction
        self.threshold_change = threshold_change
        self.window_type = window_type

    def _validate_signal(self, signal: np.ndarray) -> None:
        """
        Paranoid input sanitization: Shape, dtype, length checks.

        Args:
            signal: Input signal array

        Raises:
            ValueError: On invalid input
        """
        if not isinstance(signal, np.ndarray) or signal.ndim != 1:
            raise ValueError(
                "Signal must be 1D np.ndarray (e.g., norms.shape = (T,))."
            )

        if signal.dtype not in (np.float32, np.float64):
            signal = signal.astype(np.float64)  # Coerce safely

        if len(signal) < 32:
            raise ValueError(
                f"Signal too short (len={len(signal)}); need >=32 for FFT stability."
            )

        if np.any(~np.isfinite(signal)):
            raise ValueError(
                "Signal contains inf/NaN; sanitize upstream (e.g., clip outliers)."
            )

    def analyze(
        self,
        signal: np.ndarray,
        baseline: Optional[float] = None,
        use_complex: bool = False
    ) -> Tuple[float, float, bool]:
        """
        Core analysis: FFT → log-PSD slope on low freqs → % change vs. baseline.

        OPTIMIZED VERSION with:
        - Linear detrending (removes drift artifacts)
        - Windowing (mitigates spectral leakage)
        - Zero-frequency filtering

        Args:
            signal: 1D array of ordered norms (T points)
            baseline: Optional reference slope (from healthy prefix)
            use_complex: If True, treat as complex (I+jV); else real

        Returns:
            Tuple of (slope, percent_change, is_degraded: bool)

        Raises:
            ValueError: On invalid input or insufficient freqs
        """
        self._validate_signal(signal)

        # Optional complex handling (stub)
        if use_complex and np.issubdtype(signal.dtype, np.complexfloating):
            # Take magnitude for complex signals (common in some spectral domains)
            # This avoids the crash and provides a physical metric (Energy)
            signal = np.abs(signal)
            warnings.warn("Complex signal detected; using magnitude for spectral analysis.", UserWarning)

        # 1. Linear Detrending (Better than mean subtraction for drift)
        # Removes the linear trend so FFT focuses on fluctuations, not slope
        signal_detrended = detrend(signal, type='linear')

        # 2. Windowing (Mitigates Spectral Leakage)
        # Tapers edges to zero so the signal looks periodic to the FFT
        N = len(signal_detrended)
        window = get_window(self.window_type, N)
        signal_windowed = signal_detrended * window

        # 3. FFT & PSD
        yf = fft(signal_windowed)
        xf = fftfreq(N, 1)[:N//2]  # Positive frequencies only

        # Normalization adjustment for window energy loss
        window_norm = np.sum(window**2)
        psd = (2.0 / (N * window_norm)) * np.abs(yf[:N//2]) ** 2

        # 4. Log-Spectrum (clip to avoid log(0); numerical stability)
        log_psd = np.log10(np.clip(psd, 1e-12, None))

        # 5. Filter out the 0-frequency component if it survived detrending
        mask = xf > 0
        xf_clean = xf[mask]
        log_psd_clean = log_psd[mask]

        if len(xf_clean) < 2:
            raise ValueError("Insufficient frequencies after filtering.")

        # 6. Low-freq selection (sorted indices for lowest)
        num_low = max(2, int(len(xf_clean) * self.min_freq_fraction))
        num_low = min(num_low, len(xf_clean))  # Bounds check

        low_idx = np.argsort(xf_clean)[:num_low]
        low_x, low_y = xf_clean[low_idx], log_psd_clean[low_idx]

        if len(low_x) < 2:
            raise ValueError(f"Insufficient low freqs ({len(low_x)}).")

        # 7. Slope fit (scipy linregress: robust, low overhead)
        slope, _, r_value, _, _ = linregress(low_x, low_y)

        # Weak fit warning (not error; domain-specific)
        if r_value ** 2 < 0.5:
            warnings.warn(
                "Low R² fit on low freqs; consider longer signal.",
                UserWarning
            )

        # 8. % Change computation (safe div)
        if baseline is None:
            percent_change = 0.0
        else:
            if abs(baseline) > 1e-10:
                percent_change = abs(slope - baseline) / abs(baseline)
            else:
                percent_change = 0.0

        is_degraded = percent_change > self.threshold_change

        return slope, percent_change, is_degraded

    def monitor_sequence(
        self,
        signal: np.ndarray,
        window_size: int = 50,
        baseline_window: Optional[int] = 100
    ) -> Dict[str, any]:
        """
        Proactive monitoring: Rolling analysis for early degradation detection.
        Computes baselines from initial windows; flags on prefixes.

        Args:
            signal: Full sequence (T >= window_size + baseline_window)
            window_size: Prefix length for rolling checks (e.g., 50 paragraphs)
            baseline_window: Initial healthy baseline length (e.g., first 100)

        Returns:
            Dict with 'detections', 'changes', 'early_stop_idx'

        Raises:
            ValueError: If sequence too short
        """
        self._validate_signal(signal)

        if len(signal) < window_size + (baseline_window or 0):
            raise ValueError("Sequence too short for monitoring.")

        # Compute initial baseline
        base_start = 0
        base_end = baseline_window or len(signal) // 2
        base_signal = signal[base_start:base_end]
        base_slope, _, _ = self.analyze(base_signal)

        detections: List[bool] = []
        changes: List[float] = []

        # Overlap for sensitivity
        for i in range(window_size, len(signal) + 1, window_size // 4):
            prefix = signal[:i]
            slope, change, degraded = self.analyze(prefix, baseline=base_slope)
            detections.append(degraded)
            changes.append(change)

            if degraded:
                return {
                    'detections': detections,
                    'changes': changes,
                    'early_stop_idx': i  # Flag termination point
                }

        return {
            'detections': detections,
            'changes': changes,
            'early_stop_idx': None
        }


# Example Usage (for tests/docs; not executed in prod)
if __name__ == "__main__":
    # Synthetic test (from validation)
    np.random.seed(42)
    T = 200
    healthy = np.abs(np.cumsum(np.random.randn(T) * 0.1)) + 5.0

    fa = FourierAnalyzer()
    slope_h, _, _ = fa.analyze(healthy)
    print(f"Healthy baseline slope: {slope_h:.4f}")

    # Corrupt: <1% change (local outliers)
    corrupt = healthy.copy()
    corrupt[99:102] += 0.05 + np.random.randn(3) * 0.1
    _, change_c, deg_c = fa.analyze(corrupt, baseline=slope_h)
    print(f"Local Corrupt: {change_c:.4f} change, Degraded: {deg_c}")

    # Degraded: >1% (global degradation)
    degraded = healthy.copy()
    noise_ramp = np.linspace(0, 1, 80)
    degraded[120:] += np.random.randn(80) * noise_ramp * 2.0
    _, change_d, deg_d = fa.analyze(degraded, baseline=slope_h)
    print(f"Global Degraded: {change_d:.4f} change, Degraded: {deg_d}")

    # Early stop monitoring
    monitor = fa.monitor_sequence(degraded)
    print(f"Early Stop at: {monitor['early_stop_idx']}")

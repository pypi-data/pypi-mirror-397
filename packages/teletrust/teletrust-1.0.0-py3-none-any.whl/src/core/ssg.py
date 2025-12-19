"""
Symbolic Spectral Grammar (SSG) text fingerprint.

Alphabet:
    1–26 : 'a'–'z'
    27   : OTHER (space, punctuation, 0, non-alnum, etc.)
    28–36: digits '1'–'9'

Grammar:
    prime         = single, isolated letter (not equal to previous or next)
    even          = repeated consonant letter (bigram: cc, tt, ll, etc.)
    odd_composite = repeated vowel letter (bigram: aa, ee, oo, etc.)

Output:
    Fixed-length log-spectral fingerprint vector.
"""

from __future__ import annotations

import unicodedata
from typing import Dict, Tuple, Union
import numpy as np


# --------------------
# Exceptions
# --------------------

class StateDefinitionError(ValueError):
    """Raised when state definitions contain degenerate or invalid ranges."""
    pass


# --------------------
# Validation Helpers
# --------------------

def validate_state_definitions(
    state_definitions: Dict[str, Tuple[Union[int, float], Union[int, float]]]
) -> None:
    """
    Validate state definitions to prevent degenerate ranges.

    Each state is defined as a tuple (low, high) representing an energy range.
    A degenerate range occurs when high <= low, which would cause:
    - Division-by-zero in normalization
    - Infinite loops in quantization
    - Incorrect state assignment

    Parameters
    ----------
    state_definitions : dict
        Mapping of state names to (low, high) tuples.
        Example: {"Q": (0, 10.5), "T": (10.5, 50.2), "H": (50.2, 1e18)}

    Raises
    ------
    StateDefinitionError
        If any state has high <= low (degenerate range)
        If state_definitions is empty
        If values are not numeric

    Examples
    --------
    >>> validate_state_definitions({"Q": (0, 10), "T": (10, 50), "H": (50, 9999)})
    # Passes silently

    >>> validate_state_definitions({"BAD": (10, 5)})
    StateDefinitionError: Degenerate state range for 'BAD': high (5) <= low (10)
    """
    if not state_definitions:
        raise StateDefinitionError(
            "State definitions cannot be empty. "
            "Expected at least one state with (low, high) range."
        )

    for state_name, (low, high) in state_definitions.items():
        # Type check
        if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
            raise StateDefinitionError(
                f"Invalid range type for state '{state_name}': "
                f"expected numeric (low, high), got ({type(low).__name__}, {type(high).__name__})"
            )

        # NaN check
        if np.isnan(low) or np.isnan(high):
            raise StateDefinitionError(
                f"NaN detected in state '{state_name}' range: ({low}, {high}). "
                "State definitions must contain valid numeric values."
            )

        # Degenerate range guard (the key check from the TODO)
        if high <= low:
            raise StateDefinitionError(
                f"Degenerate state range for '{state_name}': "
                f"high ({high}) <= low ({low}). "
                "High boundary must be strictly greater than low boundary."
            )

# --------------------
# Encoding
# --------------------

VOWELS = set("aeiou")
VOWEL_INDICES = {ord(c) - ord("a") + 1 for c in VOWELS}  # {1,5,9,15,21}


def encode_text_to_symbols(text: str) -> np.ndarray:
    """
    Map raw text to integer symbols:

    - 'a'..'z' -> 1..26
    - '1'..'9' -> 28..36
    - everything else -> 27 (OTHER)

    Safety:
    - Normalizes text via NFKC to handle composite chars.
    - Explicitly routes non-Latin/Cyrillic to 27 to prevent crashes.
    """
    # 1. Normalize unicode (e.g. decompose accents, unify compatibility chars)
    text = unicodedata.normalize("NFKC", text)

    symbols = []

    for ch in text:
        ch_low = ch.lower()
        # 2. Safe bucket logic
        if "a" <= ch_low <= "z":
            idx = ord(ch_low) - ord("a") + 1  # 1..26
        elif "1" <= ch_low <= "9":
            idx = 27 + int(ch_low)  # 28..36
        else:
            # Covers space, punctuation, 0, AND Cyrillic/CJK/Emoji
            idx = 27  # OTHER
        symbols.append(idx)

    if not symbols:
        return np.zeros(0, dtype=int)

    return np.asarray(symbols, dtype=int)


# --------------------
# Grammar: prime / even / odd-composite
# --------------------

def compute_prime_even_odd_series(symbols: np.ndarray) -> Dict[str, np.ndarray]:
    """
    Given a 1D symbol array, compute three binary sequences:

    prime         : single, isolated letter (1..26) not equal to previous or next
    even          : repeated consonant letter (1..26, not vowel), s_t == s_{t-1}
    odd_composite : repeated vowel letter (1..26, in VOWEL_INDICES), s_t == s_{t-1}
    """
    T = int(symbols.shape[0])
    prime = np.zeros(T, dtype=float)
    even = np.zeros(T, dtype=float)
    odd_comp = np.zeros(T, dtype=float)

    if T == 0:
        return {"prime": prime, "even": even, "odd_composite": odd_comp}

    for t in range(T):
        s = int(symbols[t])
        prev_s = int(symbols[t - 1]) if t > 0 else None
        next_s = int(symbols[t + 1]) if t < T - 1 else None

        # Repeated letters (even / odd_composite)
        if t > 0 and 1 <= s <= 26 and s == prev_s:
            if s in VOWEL_INDICES:
                odd_comp[t] = 1.0
            else:
                even[t] = 1.0

        # Prime = single, isolated letter (1..26, not equal to previous or next)
        if 1 <= s <= 26:
            cond_prev = (prev_s is None) or (prev_s != s)
            cond_next = (next_s is None) or (next_s != s)
            if cond_prev and cond_next:
                prime[t] = 1.0

    return {"prime": prime, "even": even, "odd_composite": odd_comp}


# --------------------
# Spectrum
# --------------------

# Hann window fallback for scipy/numpy compatibility
try:
    from scipy.signal.windows import hann as scipy_hann
    _HANN_AVAILABLE = True
except ImportError:
    try:
        from scipy.signal import hann as scipy_hann
        _HANN_AVAILABLE = True
    except ImportError:
        scipy_hann = None
        _HANN_AVAILABLE = False


def _get_hann_window(length: int) -> np.ndarray:
    """
    Get Hann window of specified length.

    Falls back to numpy implementation if scipy unavailable.
    """
    if _HANN_AVAILABLE and scipy_hann is not None:
        return scipy_hann(length)
    else:
        # NumPy fallback (np.hanning deprecated in 1.26+, but still works)
        return np.hanning(length)


def _log_spectrum(x: np.ndarray,
                  max_freq: float = 0.5,
                  n_bins: int = 64,
                  apply_window: bool = True) -> np.ndarray:
    """
    Compute a log10-magnitude spectrum summary for a real-valued 1D signal.

    Steps:
        1) Remove DC (subtract mean).
        2) Apply Hann window (mitigates Gibbs ringing / spectral leakage).
        3) Real FFT (np.fft.rfft).
        4) Take |FFT|, add epsilon, log10.
        5) Keep frequencies in [0, max_freq].
        6) Downsample / interpolate to n_bins.

    Parameters
    ----------
    x : np.ndarray
        Input signal.
    max_freq : float
        Maximum frequency fraction to keep (0.5 = Nyquist).
    n_bins : int
        Number of output frequency bins.
    apply_window : bool
        If True, apply Hann window before FFT (default True).

    Returns
    -------
    np.ndarray
        1D array of length n_bins.
    """
    T = int(x.shape[0])
    if T == 0:
        return np.zeros(n_bins, dtype=float)

    # Remove DC
    x_centered = x - x.mean()

    # Apply Hann window to mitigate spectral leakage (Checklist Phase 1.1)
    if apply_window and T > 1:
        window = _get_hann_window(T)
        x_windowed = x_centered * window
    else:
        x_windowed = x_centered

    # Real FFT
    X = np.fft.rfft(x_windowed)
    mag = np.abs(X)

    # Frequency axis
    freqs = np.fft.rfftfreq(T, d=1.0)

    # Restrict to [0, max_freq]
    mask = freqs <= max_freq
    freqs_sel = freqs[mask]
    mag_sel = mag[mask]

    if freqs_sel.size == 0:
        return np.zeros(n_bins, dtype=float)

    # Log-scale
    eps = 1e-8
    log_mag = np.log10(mag_sel + eps)

    # Resample to n_bins via linear interpolation
    target_freqs = np.linspace(0.0, min(max_freq, freqs_sel[-1]), num=n_bins)
    log_mag_resampled = np.interp(target_freqs, freqs_sel, log_mag)

    return log_mag_resampled.astype(float)



# --------------------
# Entropy & Validation
# --------------------

def compute_symbol_entropy(symbols: np.ndarray) -> float:
    """
    Compute Shannon entropy of the symbol distribution in bits.

    H(X) = -sum(p(x) * log2(p(x)))

    Parameters
    ----------
    symbols : np.ndarray
        Array of integer symbols.

    Returns
    -------
    float
        Entropy in bits. Returns 0.0 for empty input.
    """
    if symbols.size == 0:
        return 0.0

    _, counts = np.unique(symbols, return_counts=True)
    probs = counts / symbols.size

    # Avoid log2(0) - counts are always > 0 from unique
    entropy = -np.sum(probs * np.log2(probs))
    return entropy


def validate_input_entropy(symbols: np.ndarray, min_entropy: float = 1.5) -> float:
    """
    Validate that the input symbol stream has sufficient specific entropy.

    Low entropy indicates repetitive, low-information input (e.g. "aaaaa")
    which does not support robust spectral fingerprinting.

    Parameters
    ----------
    symbols : np.ndarray
        Encoded text symbols.
    min_entropy : float
        Minimum required entropy in bits (default 1.5).

    Returns
    -------
    float
        The computed entropy.

    Raises
    ------
    ValueError
        If entropy is below the threshold.
    """
    entropy = compute_symbol_entropy(symbols)
    if entropy < min_entropy:
        raise ValueError(
            f"Input text entropy ({entropy:.2f} bits) is below minimum threshold "
            f"({min_entropy} bits). Input is too repetitive for spectral analysis."
        )
    return entropy


# --------------------
# Public API
# --------------------

def compute_ssg_fingerprint(
    text: str,
    max_freq: float = 0.5,
    n_bins: int = 64,
) -> np.ndarray:
    """
    Compute the Symbolic Spectral Grammar (SSG) fingerprint for a text.

    Pipeline:
        1) Encode text -> symbol indices.
        2) Validate entropy (>1.5 bits).
        3) Compute prime/even/odd-composite binary series.
        4) Compute log-spectrum summary for each series.
        5) Concatenate into a single feature vector.

    Returns:
        1D numpy array of length 3 * n_bins:
            [prime_spectrum, even_spectrum, odd_composite_spectrum]
    """
    symbols = encode_text_to_symbols(text)

    # Validation step (Checklist Phase 1.2)
    validate_input_entropy(symbols, min_entropy=1.5)

    series = compute_prime_even_odd_series(symbols)

    prime_spec = _log_spectrum(series["prime"], max_freq=max_freq, n_bins=n_bins)
    even_spec = _log_spectrum(series["even"], max_freq=max_freq, n_bins=n_bins)
    odd_spec = _log_spectrum(series["odd_composite"], max_freq=max_freq, n_bins=n_bins)

    # Concatenate in a fixed order
    fingerprint = np.concatenate([prime_spec, even_spec, odd_spec], axis=0)

    return fingerprint

# --------------------
# Main Execution Block
# --------------------

if __name__ == "__main__":
    # Test strings designed to trigger specific grammar rules
    test_samples = [
        "Hello World",              # 'll' (even), isolated letters (prime)
        "baaa baaa black sheep",    # 'aaa', 'ee' (odd_composite), 'bb', 'ss' are separate
        "Mississippi",              # 'ss', 'ss', 'pp' (even)
        "123456789",                # Digits, primes depend on surroundings
    ]

    print("--- SSG Fingerprint Test ---\n")

    for text in test_samples:
        print(f"Input: '{text}'")

        # 1. Inspect encoded symbols
        syms = encode_text_to_symbols(text)
        print(f"Symbols: {syms}")

        # 2. Inspect binary series logic
        series = compute_prime_even_odd_series(syms)
        print(f"Primes (indices): {np.where(series['prime'] == 1)[0]}")
        print(f"Evens (indices):  {np.where(series['even'] == 1)[0]}")
        print(f"Odds (indices):   {np.where(series['odd_composite'] == 1)[0]}")

        # 3. Compute Full Fingerprint
        fp = compute_ssg_fingerprint(text, n_bins=10) # Reduced bins for display
        print(f"Fingerprint (First 10 of {len(fp)}): {fp[:10]}")
        print("-" * 40)

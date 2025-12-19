"""
Golden Dataset Module
---------------------
Phase 7: Validation Data Management

Responsibilities:
1. Synthetic Data Generation (Sine, Chirp, Noise)
2. Golden Dataset Ingestion (GRACE-FO / CSV)
3. Validation Schema Enforcement
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List

@dataclass
class ValidationConfig:
    random_seed: int = 42
    test_split: float = 0.3
    chirp_f0: float = 0.1
    chirp_f1: float = 0.4
    noise_level: float = 0.1

class SyntheticGenerator:
    """Generates synthetic signals for codec verification."""

    def __init__(self, config: ValidationConfig):
        self.config = config
        self.rng = np.random.default_rng(config.random_seed)

    def generate_sine_wave(self, n_points: int, freq: float = 5.0) -> np.ndarray:
        """Generate pure sine wave + noise."""
        t = np.linspace(0, 1, n_points, endpoint=False)
        signal = np.sin(2 * np.pi * freq * t)
        noise = self.rng.standard_normal(n_points) * self.config.noise_level
        return signal + noise

    def generate_chirp(self, n_points: int) -> np.ndarray:
        """Generate precision chirp signal (transient detection)."""
        t = np.linspace(0, 1, n_points, endpoint=False)
        # linear chirp: f(t) = f0 + (f1-f0)*t
        # phase phi(t) = integral(f(tau) dtau) = f0*t + 0.5*(f1-f0)*t^2
        f0, f1 = self.config.chirp_f0, self.config.chirp_f1
        phase = 2 * np.pi * (f0 * t + 0.5 * (f1 - f0) * t**2)
        signal = np.sin(phase)
        return signal

    def generate_anomaly(self, n_points: int, anomaly_type: str = "spike") -> np.ndarray:
        """Generate signal with injected anomaly."""
        signal = self.generate_sine_wave(n_points)
        idx = n_points // 2

        if anomaly_type == "spike":
            signal[idx] += 5.0
        elif anomaly_type == "dead":
            signal[idx:idx+10] = 0.0

        return signal

class GoldenDatasetLoader:
    """Ingests and validates real-world Golden Datasets (e.g., GRACE-FO)."""

    REQUIRED_COLUMNS = {"lat", "lon", "alt", "gravity_anomaly"}

    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> pd.DataFrame:
        """Load and validate dataset."""
        try:
            if self.file_path.endswith(".csv"):
                df = pd.read_csv(self.file_path)
            elif self.file_path.endswith(".parquet"):
                df = pd.read_parquet(self.file_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or Parquet.")

            self._validate_schema(df)
            return df
        except Exception as e:
            raise RuntimeError(f"Failed to load Golden Dataset: {e}")

    def _validate_schema(self, df: pd.DataFrame) -> None:
        """Ensure strict schema compliance."""
        missing = self.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Type checks
        for col in self.REQUIRED_COLUMNS:
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise TypeError(f"Column '{col}' must be numeric")

def split_dataset(data: np.ndarray, split_ratio: float = 0.3) -> Tuple[np.ndarray, np.ndarray]:
    """Train/Test split helper."""
    n_test = int(len(data) * split_ratio)
    return data[:-n_test], data[-n_test:]

if __name__ == "__main__":
    print("--- Golden Dataset Generator Test ---")
    gen = SyntheticGenerator(ValidationConfig())
    wave = gen.generate_sine_wave(100)
    print(f"Generated Sine (first 5): {wave[:5]}")

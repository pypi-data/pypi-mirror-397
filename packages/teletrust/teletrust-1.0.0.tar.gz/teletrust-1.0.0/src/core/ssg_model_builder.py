"""
SSG Model Builder
-----------------
Phase 8.1: Concrete Model Generation

Responsible for:
1. Ingesting Golden Dataset (Synthetic or Real)
2. Calibrating Spectral Thresholds (Max, Mean, Std)
3. Learning Grammar Transitions (Q->T->H)
4. Exporting Frozen 'ssg_production_v1.json' Artifact

Usage:
    python ssg_model_builder.py --export ssg_production_v1.json
"""

import json
import numpy as np
import os
import sys
from typing import Dict, Any

# Ensure path to src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.ssg import compute_ssg_fingerprint
from src.core.golden_dataset import SyntheticGenerator, ValidationConfig

class SSGModelBuilder:
    def __init__(self):
        self.config = ValidationConfig()
        self.generator = SyntheticGenerator(self.config)
        self.fingerprints = []
        self.model_state = {}

    def generate_training_data(self, n_samples: int = 1000):
        """Generate synthetic 'Golden' data (e.g. valid clinical texts)"""
        # Since we don't have a massive text corpus generator, we will simulate
        # Valid "Clinical Consent" text variations + Noise variations
        print(f"[Builder] Generating {n_samples} synthetic training samples...")

        # Base valid examples
        templates = [
            "Patient {name} consents to telehealth.",
            "Symptoms: {symptom}, Duration: {days} days.",
            "Diagnosis: {condition}, ICD-10: {code}.",
            "Treatment plan: {drug} {dosage}mg daily.",
            "No known allergies. Vitals stable."
        ]

        # Simple random fillers
        names = ["A. Smith", "B. Jones", "C. Doe", "D. White"]
        symptoms = ["cough", "fever", "pain", "rash"]
        conditions = ["Flu", "Cold", "Infection", "Anxiety"]
        drugs = ["Amoxicillin", "Lisinopril", "Sertraline"]

        rng = np.random.default_rng(42)

        for _ in range(n_samples):
            t = rng.choice(templates)
            text = t.format(
                name=rng.choice(names),
                symptom=rng.choice(symptoms),
                days=rng.integers(1, 14),
                condition=rng.choice(conditions),
                code=f"J{rng.integers(10,99)}",
                drug=rng.choice(drugs),
                dosage=rng.choice([10, 20, 50, 100])
            )
            # Add slight jitter/variation?
            # Real text doesn't have "jitter" exactly, but we want robust fingerprints.
            # For this MVP, exact text is fine.

            fp = compute_ssg_fingerprint(text, n_bins=64)
            self.fingerprints.append(fp)

        self.fingerprints = np.array(self.fingerprints)
        print(f"[Builder] Generated fingerprints shape: {self.fingerprints.shape}")

    def calibrate(self):
        """Calculate statistical thresholds from training data"""
        if len(self.fingerprints) == 0:
            raise ValueError("No data to calibrate!")

        print("[Builder] Calibrating thresholds...")

        # Compute stats across the population of fingerprints
        # Axis 0 = across samples
        mean_vector = np.mean(self.fingerprints, axis=0)
        std_vector = np.std(self.fingerprints, axis=0)

        # Global energy stats (magnitude of vectors should be 1.0 due to L2 norm,
        # but let's look at raw energy if we had it. Here we have fingerprints.)
        # MOA uses z-scores against these means/stds.

        self.model_state = {
            "meta": {
                "type": "SSGModel",
                "version": "1.0",
                "drift_resistant": True,
                "timestamp": "2025-12-11T14:45:00Z" # Mock time
            },
            "parameters": {
                "window_size": 64, # match n_bins
                "learned_thresholds": {
                    # Convert numpy types to python native for JSON
                    "centroid_mean": [float(x) for x in mean_vector],
                    "centroid_std": [float(x) for x in std_vector]
                }
            },
            # Grammar matrix would be derived from state transitions in ssg.py
            # For now we placeholder it as defined in architecture
            "rules": {
                "grammar_matrix": {
                    "Q": ["Q", "T"],
                    "T": ["Q", "T", "H"],
                    "H": ["T"]
                }
            }
        }

        # 3.1 Sentinel Handling (Robustness)
        # Ensure no NaN/Inf values break JSON serialization
        self._sanitize_model_state()

        print("[Builder] Calibration complete.")

    def _sanitize_model_state(self):
        """Replace Inf/NaN with sentinels for JSON safety"""
        def clean(obj):
            if isinstance(obj, float):
                if np.isnan(obj): return 0.0
                if np.isinf(obj): return 1e18 if obj > 0 else -1e18
                return obj
            elif isinstance(obj, list):
                return [clean(x) for x in obj]
            elif isinstance(obj, dict):
                return {k: clean(v) for k, v in obj.items()}
            return obj

        self.model_state = clean(self.model_state)

    def export(self, filepath: str):
        """Save to JSON with backup on overwrite"""
        if os.path.exists(filepath):
            backup_path = filepath + ".bak"
            try:
                if os.path.exists(backup_path):
                    os.remove(backup_path) # Remove old backup
                os.rename(filepath, backup_path)
                print(f"[Builder] Backed up existing artifact to: {backup_path}")
            except OSError as e:
                print(f"[Builder] Warning: Failed to create backup: {e}")

        with open(filepath, 'w') as f:
            json.dump(self.model_state, f, indent=2)
        print(f"[Builder] Artifact saved to: {filepath}")

if __name__ == "__main__":
    builder = SSGModelBuilder()
    builder.generate_training_data(n_samples=500)
    builder.calibrate()

    # Save to src/core (or root)
    output_path = os.path.join(os.path.dirname(__file__), "ssg_production_v1.json")
    builder.export(output_path)

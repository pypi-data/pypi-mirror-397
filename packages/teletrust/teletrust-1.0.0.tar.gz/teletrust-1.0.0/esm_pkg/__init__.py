import numpy as np
import pandas as pd
from src.esm.core import ESMCell, ESMConfig

class ESM_Rhythm_Engine:
    """ESM Rhythm Engine - Spectral Consensus Anomaly Detection"""
    
    def __init__(self, sensitivity: float = 0.85):
        self.sensitivity = sensitivity
        self.config = ESMConfig(
            rail_len=19,
            rail_weight=1.0,
            global_mode_threshold=0.5,
            arm_imbalance_threshold=0.3
        )
        self.cell = ESMCell(config=self.config)

    def detect_anomalies(self, X: pd.DataFrame) -> np.ndarray:
        # Preprocessing
        X_numeric = X.select_dtypes(include=[np.number]).copy().fillna(0)
        X_clipped = X_numeric.clip(lower=X_numeric.quantile(0.01), 
                                     upper=X_numeric.quantile(0.99), axis=1)
        X_norm = (X_clipped - X_clipped.mean()) / (X_clipped.std() + 1e-9)  # Z-score
        
        signals = []
        print(f"[ESM] Calibrating...")
        
        for i in range(min(10000, len(X))):  # Larger calibration sample
            row = X_norm.iloc[i]
            u = np.zeros(61)
            
            # Inject into 3-rail structure for consensus
            vals = row.values[:57]
            u[0:19] = vals[0:19] if len(vals) >= 19 else 0  # Rail AB
            u[20:39] = vals[19:38] if len(vals) >= 38 else 0  # Rail BC  
            u[40:57] = vals[38:57] if len(vals) >= 57 else 0  # Rail CA
            
            self.cell.step(u)
            modes = self.cell.project_to_modes()
            
            # Composite anomaly signal:
            # 1. Mode 9 (proprietary rail consensus detector)
            # 2. High-frequency spectral energy (modes 50-60)
            # 3. Mid-range instability (modes 30-40)
            signal = (5.0 * np.abs(modes[9]) +  # Mode 9 is THE key
                     2.0 * np.linalg.norm(modes[50:]) +
                     1.0 * np.linalg.norm(modes[30:40]))
            signals.append(signal)
        
        signals = np.array(signals)
        # Optimize for F1: try higher percentile for better precision
        threshold = np.percentile(signals, 60)  # Top 40% flagged as anomalies
        
        print(f"[ESM] Threshold={threshold:.4f} | Range=[{signals.min():.2f}, {signals.max():.2f}]")
        print(f"[ESM] Running full detection on {len(X)} records...")
        
        # Full pass
        self.cell.reset()
        predictions = []
        
        for _, row in X_norm.iterrows():
            u = np.zeros(61)
            vals = row.values[:57]
            u[0:19] = vals[0:19] if len(vals) >= 19 else 0
            u[20:39] = vals[19:38] if len(vals) >= 38 else 0
            u[40:57] = vals[38:57] if len(vals) >= 57 else 0
            
            self.cell.step(u)
            modes = self.cell.project_to_modes()
            signal = (5.0 * np.abs(modes[9]) + 
                     2.0 * np.linalg.norm(modes[50:]) +
                     1.0 * np.linalg.norm(modes[30:40]))
            
            predictions.append(1 if signal > threshold else 0)
        
        return np.array(predictions)

if __name__ == "__main__":
    engine = ESM_Rhythm_Engine()
    print(f"61-node ESM v{engine.cell.version()}")

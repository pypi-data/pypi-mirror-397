"""
esm/baseline_store.py
=====================
Persistent store for spectral baselines keyed by context.
Key context: (model_id, task_type, template_id, clinic_id, environment)
"""

import sqlite3
import json
import hashlib
import numpy as np
import os
from pathlib import Path
from typing import Dict, Any, Optional

class BaselineStore:
    def __init__(self, db_path: str = "./var/esm_baselines.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True, parents=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS baselines (
                    context_hash TEXT PRIMARY KEY,
                    context_json TEXT,
                    baseline_vector BLOB,
                    sample_count INTEGER,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def _hash_context(self, context: Dict[str, Any]) -> str:
        """Create a deterministic hash from context dict."""
        # Ensure canonical ordering
        canonical = json.dumps(context, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def get_baseline(self, context: Dict[str, Any]) -> Optional[np.ndarray]:
        """Retrieve baseline for a given context."""
        ctx_hash = self._hash_context(context)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT baseline_vector FROM baselines WHERE context_hash = ?", (ctx_hash,))
            row = cur.fetchone()
            if row:
                return np.frombuffer(row[0])
        return None

    def update_baseline(self, context: Dict[str, Any], new_vector: np.ndarray):
        """Update or create baseline using a simple moving average or replacement."""
        ctx_hash = self._hash_context(context)
        vec_blob = new_vector.tobytes()
        ctx_json = json.dumps(context)
        
        with sqlite3.connect(self.db_path) as conn:
            # Check if exists
            cur = conn.execute("SELECT sample_count, baseline_vector FROM baselines WHERE context_hash = ?", (ctx_hash,))
            row = cur.fetchone()
            
            if row:
                count, old_blob = row
                old_vec = np.frombuffer(old_blob)
                # Weighted update (EMA-like)
                updated_vec = (old_vec * count + new_vector) / (count + 1)
                conn.execute("""
                    UPDATE baselines 
                    SET baseline_vector = ?, sample_count = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE context_hash = ?
                """, (updated_vec.tobytes(), count + 1, ctx_hash))
            else:
                conn.execute("""
                    INSERT INTO baselines (context_hash, context_json, baseline_vector, sample_count)
                    VALUES (?, ?, ?, ?)
                """, (ctx_hash, ctx_json, vec_blob, 1))

if __name__ == "__main__":
    # Test
    store = BaselineStore("./var/test_baselines.db")
    ctx = {"model": "gpt-4", "task": "telehealth_audit"}
    vec = np.random.rand(192)
    store.update_baseline(ctx, vec)
    retrieved = store.get_baseline(ctx)
    assert np.allclose(vec, retrieved)
    print("BaselineStore check passed.")
    if os.path.exists("./var/test_baselines.db"):
        os.remove("./var/test_baselines.db")

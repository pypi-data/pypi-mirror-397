"""
esm/audit.py
============
Hash-chained audit log for ESM decisions (Pass/Warn/Block).
Ensures tamper-evident records of governance outcomes.
"""

import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional

class ESMAuditor:
    def __init__(self, log_path: str = "./var/esm_audit_chain.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(exist_ok=True, parents=True)
        self.last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Recover the last hash from the audit file if it exists."""
        if not self.log_path.exists():
            return "0" * 64 # Genesis hash
            
        try:
            with open(self.log_path, "rb") as f:
                # Seek to last line
                f.seek(0, 2)
                if f.tell() == 0: return "0" * 64
                
                # Rudimentary tail
                f.seek(-1024, 2) if f.tell() > 1024 else f.seek(0)
                lines = f.read().decode().strip().split('\n')
                if not lines: return "0" * 64
                
                last_entry = json.loads(lines[-1])
                return last_entry.get("hash", "0" * 64)
        except Exception:
            return "0" * 64

    def log_decision(self, feature_vector: Any, decision: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record a decision in the hash-chained log.
        """
        # Convert feature vector to hash for storage efficiency
        if hasattr(feature_vector, "tobytes"):
            vec_repr = hashlib.sha256(feature_vector.tobytes()).hexdigest()
        else:
            vec_repr = str(feature_vector)
            
        entry = {
            "prev_hash": self.last_hash,
            "timestamp": time.time(),
            "feature_hash": vec_repr,
            "decision": decision,
            "context": context
        }
        
        # Deterministic entry hash
        entry_json = json.dumps(entry, sort_keys=True)
        entry["hash"] = hashlib.sha256(entry_json.encode()).hexdigest()
        
        # Update state and persist
        self.last_hash = entry["hash"]
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            
        return entry

if __name__ == "__main__":
    # Test
    auditor = ESMAuditor("./var/test_audit.jsonl")
    ctx = {"clinic": "A1"}
    auditor.log_decision([1, 2, 3], "PASS", ctx)
    auditor.log_decision([4, 5, 6], "BLOCK", ctx)
    print(f"Audit chain tail hash: {auditor.last_hash}")
    import os
    if os.path.exists("./var/test_audit.jsonl"):
        os.remove("./var/test_audit.jsonl")

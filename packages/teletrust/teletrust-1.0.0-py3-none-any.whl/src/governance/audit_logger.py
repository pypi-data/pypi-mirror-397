import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

# Import Codec (unchanged)
try:
    from src.physics.prime_codecs import encode_macro_state, ESMPrimeStateCodec
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.physics.prime_codecs import encode_macro_state, ESMPrimeStateCodec

class AuditLogger:
    def __init__(self, log_path: str = "var/audit/moa_audit.jsonl", n_nodes: int = 61):
        self.log_path = Path(log_path)
        self.n_nodes = n_nodes
        self.node_codec = ESMPrimeStateCodec(n_nodes)

        if self.log_path.parent != Path('.'):
             self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self.ops_logger = logging.getLogger("moa_ops")
        self.last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Read the last line of the log to get the previous hash."""
        if not self.log_path.exists():
            return "GENESIS"
        try:
            with open(self.log_path, "rb") as f:
                # Efficiently read last line - for now simple readlines is fine for MVP size
                lines = f.readlines()
                if not lines: return "GENESIS"
                last = json.loads(lines[-1])
                return last.get("entry_hash", "GENESIS")
        except Exception:
            return "BROKEN_CHAIN"

    def log_state(self, step: int, macro_bins: Tuple[int, int, int], node_mask: List[bool], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            macro_code = encode_macro_state(*macro_bins)
            node_code = self.node_codec.encode_state(node_mask)

            entry = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "step": step,
                "macro_code": macro_code,
                "node_code_hex": hex(node_code),
                "prev_hash": self.last_hash
            }

            if metadata:
                if "session_hash" in metadata:
                    entry["session_hash"] = metadata["session_hash"]

            # Canonical JSON string for hashing
            # separators=(',', ':') removes whitespace for consistent hashing
            entry_str = json.dumps(entry, sort_keys=True, separators=(',', ':'))

            # Compute Hash
            entry_hash = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
            entry["entry_hash"] = entry_hash

            # Write
            with open(self.log_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            self.last_hash = entry_hash
            return entry

        except Exception as e:
            self.ops_logger.error(f"Failed to log audit entry at step {step}: {e}")
            raise e

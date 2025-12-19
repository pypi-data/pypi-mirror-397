"""
Test Audit Logger
=================
Verifies that:
1. Audit logs are written to disk.
2. Prime Gödel Codes decode back to the original input.
3. Micro-state masks are preserved exactly.
"""

import unittest
import json
import os
from pathlib import Path
import sys

# Add workspace root to path
ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT))

from moa_telehealth_governor.src.governance.audit_logger import AuditLogger
from src.esm.codec import MacroStateCodec, ESMPrimeStateCodec

class TestAuditLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = "test_esm_audit.log"
        # Clean up previous run
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

        self.logger = AuditLogger(log_path=self.log_file, n_nodes=61)

    def tearDown(self):
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_end_to_end_logging(self):
        """Log a state, read it back, decode it, compare."""

        # 1. Define inputs
        step = 101
        macro_bins = (2, 5, 0) # Activity=2, Entropy=5, Pattern=0

        # Mask: Core nodes (0-20) ON, plus some others
        mask = [False] * 61
        for i in range(21): mask[i] = True # Core
        mask[50] = True # Toggle member
        mask[60] = True # Toggle member

        # 2. Log it
        entry = self.logger.log_state(step, macro_bins, mask)

        # 3. Read it back
        with open(self.log_file, "r") as f:
            line = f.readline()
            saved_entry = json.loads(line)

        # 4. Verify fields
        self.assertEqual(saved_entry["step"], step)
        self.assertEqual(saved_entry["macro_code"], entry["macro_code"])
        self.assertEqual(saved_entry["node_code_hex"], entry["node_code_hex"])

        # 5. Verify DECIPHERABILITY (The key requirement)
        # Macro
        decoded_bins = MacroStateCodec.decode(saved_entry["macro_code"])
        self.assertEqual(decoded_bins, macro_bins)

        # Micro
        node_code = int(saved_entry["node_code_hex"], 16)
        decoded_mask = ESMPrimeStateCodec(61).decode(node_code)
        self.assertEqual(decoded_mask, mask)

        print("\n[PASS] Prime Gödel Codec Round-Trip Verified!")
        print(f"      Macro Code: {saved_entry['macro_code']}")
        print(f"      Node Code (First 10 char): {saved_entry['node_code_hex'][:10]}...")

if __name__ == "__main__":
    unittest.main()

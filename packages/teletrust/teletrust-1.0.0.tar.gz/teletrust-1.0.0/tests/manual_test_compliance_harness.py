
import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.compliance.engine import ComplianceEngine

class TestComplianceHarness(unittest.TestCase):
    def setUp(self):
        self.engine = ComplianceEngine()

    @patch('requests.get')
    def test_icd10_validation_valid(self, mock_get):
        # Mock NIH API response for Valid Code
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        # [count, codes, null, [[code, desc]]]
        mock_resp.json.return_value = [1, ["F32.9"], None, [["F32.9", "MDD, unspecified"]]]
        mock_get.return_value = mock_resp

        ctx = {"diagnosis_codes": ["F32.9"]}
        res = self.engine.evaluate(ctx)

        self.assertNotEqual(res.verdict, "DENY")
        self.assertTrue(res.icd_validation[0]["valid"])

    @patch('requests.get')
    def test_icd10_validation_invalid(self, mock_get):
        # Mock NIH API response for Invalid Code
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [0, [], None, []]
        mock_get.return_value = mock_resp

        ctx = {"diagnosis_codes": ["XYZ.99"]}
        res = self.engine.evaluate(ctx)

        self.assertEqual(res.verdict, "DENY")
        self.assertIn("Invalid ICD-10", res.reason)

    def test_pos_logic_home(self):
        """Test strict POS 10 logic for 'home'."""
        ctx = {"patient_location": "home / residence", "service_mode": "video"}
        res = self.engine.evaluate(ctx)
        self.assertEqual(res.billing["pos"], "10")
        # Check evidence contains CMS hash
        self.assertTrue(any("stubbed-hash-cms-pos10" in e.get("pin", "") for e in res.evidence))

    def test_pos_logic_clinic(self):
        """Test strict POS 02 logic for 'other'."""
        ctx = {"patient_location": "clinic", "service_mode": "video"}
        res = self.engine.evaluate(ctx)
        self.assertEqual(res.billing["pos"], "02")
        self.assertTrue(any("stubbed-hash-cms-pos02" in e.get("pin", "") for e in res.evidence))

    def test_fl_registration(self):
        """Verify FL registration rules still apply."""
        ctx = {
            "patient_state": "FL",
            "provider_home_state": "NY",
            "provider_type": "MD",
            "service_mode": "video"
        }
        res = self.engine.evaluate(ctx)
        self.assertEqual(res.verdict, "DENY")

        # Add registration
        ctx["telehealth_registration_number"] = "T-123"
        res2 = self.engine.evaluate(ctx)
        self.assertEqual(res2.verdict, "ALLOW")

if __name__ == "__main__":
    unittest.main()

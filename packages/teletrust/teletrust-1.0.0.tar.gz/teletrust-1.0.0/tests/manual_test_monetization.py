
import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.phi_guard import PhiGuard
from src.reg_gateway.server import lookup_ecfr, lookup_nlm_codes
from src.billing.stripe_integration import meter_usage

class TestMonetizationComponents(unittest.TestCase):

    def test_phi_guard_detection(self):
        msg = "Patient John Doe (SSN: 123-45-6789) called."
        guard = PhiGuard()
        self.assertTrue(guard.scan(msg))
        redacted = guard.redact(msg)
        self.assertIn("[REDACTED:SSN]", redacted)
        self.assertNotIn("123-45-6789", redacted)

    def test_phi_guard_clean(self):
        msg = "Patient requested a refill for aspirin."
        guard = PhiGuard()
        self.assertFalse(guard.scan(msg))

    def test_mcp_tools(self):
        # Mock requests.get for eCFR
        with unittest.mock.patch('requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.json.return_value = {
                "results": [{"title": "Title 42", "section": "410.78", "summary": "Telehealth services match"}]
            }
            mock_get.return_value = mock_resp

            res = lookup_ecfr("telehealth")
            self.assertIn("Telehealth services match", res)

        # Test Stubbed NLM
        res = lookup_nlm_codes("99213")
        self.assertIn("Office or other outpatient visit", res)

    def test_billing_hook(self):
        # We just verification the function runs without error (prints to stdout)
        try:
            meter_usage(123, "test_capability", 5)
        except Exception as e:
            self.fail(f"meter_usage raised exception: {e}")

if __name__ == "__main__":
    unittest.main()

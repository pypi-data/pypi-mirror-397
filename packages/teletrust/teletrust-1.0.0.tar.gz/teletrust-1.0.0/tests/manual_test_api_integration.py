import unittest

from fastapi.testclient import TestClient
from src.api.main import app


class TestApiIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.auth_headers = {"Authorization": "Bearer sk_example_demo"}

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "healthy", "service": "moa-telehealth-governor"})

    def test_govern_allow_context(self):
        # Valid Context (FL Reg present)
        payload = {
            "session_id": "test_api_1",
            "text": "Hello, I am ready for the consultation.",
            "context": {
                "patient_state": "FL",
                "provider_home_state": "NY",
                "provider_type": "MD",
                "service_mode": "video",
                "telehealth_registration_number": "TPMC999"
            }
        }
        response = self.client.post("/govern", json=payload, headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res["compliance_verdict"], "ALLOW")
        self.assertEqual(res["zone"], "GREEN") # Assuming budget allows

    def test_govern_deny_context(self):
        # Invalid Context (FL Reg Missing)
        payload = {
            "session_id": "test_api_2",
            "text": "Hello doc.",
            "context": {
                "patient_state": "FL",
                "provider_home_state": "NY",
                "provider_type": "MD",
                "service_mode": "video"
            }
        }
        response = self.client.post("/govern", json=payload, headers=self.auth_headers)
        self.assertEqual(response.status_code, 200) # Returns 200 OK with DENY in body
        res = response.json()
        self.assertEqual(res["compliance_verdict"], "DENY")
        self.assertIn("Blocked by Telehealth Compliance Engine", res["output_text"])

    def test_strip_log_via_api(self):
        # DSM Content
        payload = {
            "session_id": "test_api_3",
            "text": "Checking DSM.",
            "context": {
                "patient_state": "CA",
                "provider_home_state": "CA",
                "standard": "DSM",
                "dsm_excerpt": "Code 123"
            }
        }
        response = self.client.post("/govern", json=payload, headers=self.auth_headers)
        self.assertEqual(response.status_code, 200)
        res = response.json()
        self.assertEqual(res["compliance_verdict"], "ALLOW")

        # Verify v1.1 fields
        self.assertIsNotNone(res["sanitization"])
        self.assertIn("DSM", res["sanitization"]["tags"])

        self.assertIsNotNone(res["usage_events"])
        events = [e["event"] for e in res["usage_events"]]
        self.assertIn("ip_redaction", events)
        self.assertIn("telehealth_policy_eval", events)

        # Check logs for redaction (legacy check)
        self.assertTrue(any("Ledger: Recorded ip_redaction" in log for log in res["action_log"]))

if __name__ == "__main__":
    unittest.main()

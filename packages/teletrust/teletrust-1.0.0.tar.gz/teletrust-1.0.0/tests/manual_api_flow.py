import sys
import time

import requests

# Configuration
BASE_URL = "http://127.0.0.1:8000"
VALID_TOKEN = "sk_example_demo"
INVALID_TOKEN = "sk_invalid_token"

def test_health():
    print("[TEST] GET /health")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print("✅ PASS: Health check 200 OK")
        else:
            print(f"❌ FAIL: Health check {resp.status_code}")
    except Exception as e:
        print(f"❌ FAIL: Could not connect to API: {e}")
        sys.exit(1)

def test_auth_failure():
    print("[TEST] Auth Failure (Invalid Token)")
    headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
    payload = {"session_id": "test_1", "text": "Hello"}
    resp = requests.post(f"{BASE_URL}/govern", json=payload, headers=headers)
    if resp.status_code == 401:
        print("✅ PASS: Correctly rejected invalid token (401)")
    else:
        print(f"❌ FAIL: Expected 401, got {resp.status_code}")

def test_govern_success():
    print("[TEST] Govern Success (Valid Token + Human Text)")
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    # Human-like text (Entropy ~4.0)
    payload = {
        "session_id": "sess_001",
        "text": "I am having trouble with the billing portal. It gives me error 500."
    }
    resp = requests.post(f"{BASE_URL}/govern", json=payload, headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response: Zone={data['zone']}, Risk={data['risk_score']}")
        if data['zone'] == 'GREEN' or data['zone'] == 'YELLOW':
            print("✅ PASS: Valid governance response received.")
        else:
            print("⚠️ WARN: Expected GREEN/YELLOW for this text, got RED?")
    else:
        print(f"❌ FAIL: Expected 200, got {resp.status_code} - {resp.text}")

def test_govern_block():
    print("[TEST] Govern Block (Chaos/Bot Text)")
    headers = {"Authorization": f"Bearer {VALID_TOKEN}"}
    # Bot/Chaos (Entropy Low or High)
    payload = {
        "session_id": "sess_002",
        "text": "Repeat Repeat Repeat Repeat Repeat Repeat " * 10
    }
    resp = requests.post(f"{BASE_URL}/govern", json=payload, headers=headers)

    if resp.status_code == 200:
        data = resp.json()
        print(f"   Response: Zone={data['zone']}, Risk={data['risk_score']}")
        if data['zone'] == 'RED' and "block" in str(data['action_log']).lower(): # Check log implies blockage or text implies it
             if "policy" in data['output_text']:
                 print("✅ PASS: Policy block triggered (RED).")
             else:
                 print("⚠️ WARN: Zone is RED but output text doesn't explicitly say blocked?")
        else:
             print(f"❌ FAIL: Expected RED Zone + Block in logs, got Zone={data['zone']} Logs={data['action_log']}")
    else:
        print(f"❌ FAIL: Expected 200, got {resp.status_code}")

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(5) # Wait for server to be ready

    test_health()
    test_auth_failure()
    test_govern_success()
    test_govern_block()

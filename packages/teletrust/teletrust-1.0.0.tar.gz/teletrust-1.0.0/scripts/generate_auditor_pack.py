
import os
import zipfile
import datetime

def generate_pack():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pack_name = f"telehealth_auditor_evidence_{timestamp}.zip"

    files_to_include = [
        "usage_ledger.jsonl",
        "var/audit/moa_audit.jsonl",
        "requirements_lock.txt",
        "scripts/telehealth_test_pack_HASHES_v1.0.1.json",
        "scripts/usage_billing_wiring_HASHES.json",
        "RUNBOOK_TELEHEALTH_GATEWAY.md",
        "src/compliance/policy_pack_v1.0.1.json"
    ]

    print(f"Generating Auditor Evidence Pack: {pack_name}")

    try:
        with zipfile.ZipFile(pack_name, 'w') as zipf:
            for file_path in files_to_include:
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=os.path.basename(file_path))
                    print(f"  + Added: {file_path}")
                else:
                    print(f"  ! Warning: File not found: {file_path}")

        print(f"\nSuccess! Evidence Pack ({os.path.getsize(pack_name)} bytes) created.")
        print(f"Deliverable: {os.path.abspath(pack_name)}")
        return True
    except Exception as e:
        print(f"Error generating pack: {e}")
        return False

if __name__ == "__main__":
    generate_pack()

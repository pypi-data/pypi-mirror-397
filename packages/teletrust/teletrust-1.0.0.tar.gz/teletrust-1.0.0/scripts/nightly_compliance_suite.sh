#!/bin/bash
# Nightly Compliance Suite
# 1. Verify Ledger Integrity
# 2. Run Policy Tests (Compliance)
# 3. Export to Stripe

echo "Starting Nightly Compliance Run at $(date)"

# Set default env if not present
export MOA_USAGE_LEDGER_PATH=${MOA_USAGE_LEDGER_PATH:-"usage_ledger.jsonl"}

# 1. Verify Record Integrity
echo "[1/3] Verifying usage ledger integrity..."
python -c "from src.billing.moa_usage_ledger import MoaUsageLedger; l=MoaUsageLedger('$MOA_USAGE_LEDGER_PATH'); exit(0 if l.verify_integrity() else 1)"
if [ $? -ne 0 ]; then
    echo "CRITICAL: Ledger integrity check failed!"
    exit 1
fi
echo "Ledger verified."

# 2. Run Compliance Tests
echo "[2/3] Running Policy Test Pack..."
python scripts/run_policy_tests.py
if [ $? -ne 0 ]; then
    echo "CRITICAL: Compliance tests failed!"
    exit 1
fi
echo "Policy tests passed."

# 3. Stripe Export
echo "[3/3] Exporting to Stripe..."
if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "SKIPPING Stripe export: STRIPE_SECRET_KEY not set."
else
    python src/billing/stripe_meters_exporter.py
fi

echo "Nightly run complete."

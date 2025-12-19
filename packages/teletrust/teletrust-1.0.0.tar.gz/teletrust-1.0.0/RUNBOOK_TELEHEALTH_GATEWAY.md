# Runbook: Telehealth Gateway v1.1.0 (Strip+Log + Metered)

## Overview

This runbook validates the deployment of the **Telehealth Citation Gateway v1.1.0** patch.
Features:

1. **`POST /govern` Endpoint**: Enforces cross-state permissions and billing logic.
2. **Moa Usage Ledger**: Hash-chained, tamper-evident audit logs.
3. **Stripe Metering**: Export of usage events to Stripe Billing.

## Prerequisites

- Python 3.10+
- `STRIPE_SECRET_KEY` (for metering export)
- `MOA_USAGE_LEDGER_PATH` (default: `./usage_ledger.jsonl`)

## 1. Verify Integrity

Check the SHA256 of the patch artifact:

```bash
# Windows (PowerShell)
Get-FileHash telehealth_citation_gateway_v1.1.0_striplog_metered.tar.gz -Algorithm SHA256
# Expected: e8ee00cba6dcf8f69e9c530078199a195795756319ee7a60ae570e55b7f7d666
```

## 2. Installation (Simulated Unzip)

The contents have been merged into `src/`.

- `src/api/main.py` -> Gateway Entrypoint
- `src/billing/moa_usage_ledger.py` -> Ledger
- `scripts/nightly_compliance_suite.sh` -> Automation

## 3. Deployment

Start the server:

```bash
python src/api/main.py
```

Health Check:

```bash
curl http://localhost:8000/health
```

## 4. Verification

Run the nightly suite to verify all components (Policy, Ledger, Wiring):

```bash
./scripts/nightly_compliance_suite.sh
```

## 5. Stripe Export (Cron)

Schedule the export script to run nightly:

```cron
0 2 * * * cd /path/to/app && ./scripts/nightly_compliance_suite.sh >> nightly.log 2>&1
```

## 6. Troubleshooting

- **Ledger Hash Fail**: If `verify_integrity()` fails, the ledger file has been manually tampered with. Archive and start fresh.
- **Stripe 401**: Check `STRIPE_SECRET_KEY`.

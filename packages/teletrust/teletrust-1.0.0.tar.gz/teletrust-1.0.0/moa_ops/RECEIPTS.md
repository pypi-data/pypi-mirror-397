# Audit Receipt Specification

## Purpose

Define tamper-evident audit records for MOA Telehealth Governor decisions.

## Receipt Format (JSONL)

Each line in `var/audit/moa_audit.jsonl`:

```json
{
  "event_id": "uuid",
  "timestamp_utc": "ISO-8601",
  "input_receipt_hmac": "sha256(HMAC(key, input_text))",
  "session_id": "client-provided",
  "votes": {
    "physics": {"zone": "GREEN", "entropy": 4.12},
    "gate": {"risk_score": 15.0, "flags": []},
    "router": {"tier": "local", "cost": 0.002}
  },
  "final_decision": "APPROVED|REJECTED|HUMAN_REVIEW",
  "model_versions": {"esm": "1.0", "gate": "1.0"},
  "prev_entry_hash": "sha256 of previous entry",
  "entry_hash": "sha256 of this entry"
}
```

## Tamper Evidence

- Each entry includes `prev_entry_hash` (hash-chaining)
- Modifying any entry breaks the chain
- Verification: iterate log, recompute hashes, compare

## What We DO NOT Store

- Raw input text (only HMAC receipt)
- PHI/PII
- Sensitive clinical content

## Retention

- Default: 90 days
- Configurable via `MOA_AUDIT_RETENTION_DAYS`

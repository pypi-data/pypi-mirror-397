# pfSense Automation Framework Logic (v2 Hardened)

**Status:** TRL 6 (System Prototype) -> **TRL 7 Target** (Incident-Grade Control)
**Valuation:** ~$200,000 (Defensible Control Plane IP)

## 1. Overview

The pfSense Automation Framework acts as a **Physical Enforcer** for the MOA ecosystem. It provides "Air-Gap on Demand" by controlling the physical network gateway (`10.10.10.1`).

**v2 Upgrade:** Moving from "Domain Blocklists" to a **"WAN-Default-Deny State Machine"** with **replay-proof signed commands**, ensuring a compromised workstation cannot "unblock itself."

## 2. Core Architecture: Split-Control

To prevent a compromised "Master Node" from self-rescuing (issuing its own UNBLOCK command), the control plane is separated:

| Component | Role | Security Property |
|-----------|------|-------------------|
| **MOA Workstation** | **Requestor** | Can only request *tightening* of policy (e.g., `BLOCK_WAN`). Cannot request loosening. |
| **Management Node** | **Approver** | Dedicated, locked-down hardware (or 2-Man Rule) required to sign `UNBLOCK_WAN` commands. |
| **pfSense Gateway** | **Enforcer** | verify Ed25519 signature -> Check Nonce/TTL -> Apply State. |

## 3. The "State Machine" Enforcement

Instead of managing fragile domain lists, the router switches between pre-defined, immutable states.

### State A: NORMAL

- **Policy:** Standard Egress Allowed.
- **Use Case:** Patching, Research, Non-Sensitive Work.

### State B: LOCAL_ONLY (The Default for Sensitive Work)

- **Policy:** **WAN Egress DENY ALL** (Interface-wide).
- **Exceptions:** None (or strictly pinned IPs for specific APIs, blocking DoH/DoT).
- **Allow:** LAN (`10.10.10.x`) and Gateway Admin (`10.10.10.1`).

### State C: QUARANTINE (Hard Drift)

- **Policy:** **Full Isolation**. Drop all traffic (LAN + WAN).
- **Trigger:** Fourier "Hard Drift" or ESM Consensus failure.
- **Recovery:** Requires biological human intervention (console access or 2-Factor Hardware Token).

## 4. The Signed Protocol (Anti-Replay)

Commands are no longer simple API calls. They are cryptographically signed envelopes to prevent replay attacks and unauthorized issuance.

**Command Envelope:**

```json
{
  "cmd": "SET_MODE_LOCAL_ONLY",
  "scope": "PROTECTED_LAN",
  "reason": "HARD_DRIFT:sha256_hash_of_anomaly_record",
  "ts": 1734520000,
  "ttl_s": 60,
  "nonce": "128_bit_random",
  "counter": 1042,
  "sig": "ed25519_signature_of_canonical_json"
}
```

**Validation Logic (The "Lock"):**

1. **Signature:** Verify `sig` matches pinned Public Key.
2. **Freshness:** `now() - ts < ttl_s` (Prevent delayed replay).
3. **Uniqueness:** `nonce` not in recent cache (Prevent immediate replay).
4. **Ordering:** `counter > last_stored_counter` (Prevent rollback).
5. **Allowlist:** `cmd` must be a valid state transition for this key.

## 5. Commercial Value & Audit

This architecture raises the system from a "prototype" to a **defensible security product**:

- **Defensible Claim:** "Hardware gateway enforces offline mode with signed, replay-proof commands."
- **Audit Trail:**
  - **MOA Side:** Hash-chained `audit.log`.
  - **Router Side:** Tamper-evident event log (Cmd, Reason, Sig Fingerprint).
- **Incident Response:** Aligns with ORCA strategies (Containment First -> Controlled Recovery).

## 6. Implementation References

- *Alabbad, M., et al. (2024).* Hardening of network segmentation.
- *Shaked, A., et al. (2023).* Operations-informed incident response playbooks.
- *Hendrickson, J.* (n.d.). pfSense REST API Package.

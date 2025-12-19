# TeleTrust Trade Secrets

> [!CAUTION]
> This document enumerates **confidential trade secrets**. Never disclose, patent, or open-source these elements.

## 1. Rhythm Engine Calibration Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| β (decay sensitivity) | `1.5` | Tunes reaction to spectral activity changes |
| γ (activity scaling) | `0.1` | Scales activity level influence on forgetting rate |
| a₀ (baseline threshold) | `5.0` | Normalizes forgetting adjustment |

*Rationale:* These values were derived from extensive experimentation. Revealing them enables easy replication.

---

## 2. Spectral Graph Topology (61-Node Architecture)

- Specific node configuration and edge connections
- How conversational features map to the graph
- Spectral mode interpretation rules

*Rationale:* The 61-node topology is the "secret sauce" for context compression. No open-source release will include this structure.

---

## 3. Prime Gödelization Scheme (343 States)

- Mapping of conversation patterns to 343 prime-derived states
- Which primes are selected and how codes are assigned
- Injection method into state machine for consensus checks

*Rationale:* Prevents third parties from copying our consensus verification mechanism.

---

## 4. PHI Detection Heuristics

- Specific regex patterns beyond obvious/public knowledge
- NLP rules for identifying protected health information
- Hash-and-salt method for audit trails without data exposure

*Rationale:* Keeps our PHI guard from being bypassed or replicated.

---

## 5. Usage Ledger Integrity Salt

- The `MOA_AUDIT_HMAC_KEY_B64` value
- Derivation method for the key

*Rationale:* Prevents ledger forgery even if log files are accessed.

---

## Legal Protection

These items are protected under:

- **Defend Trade Secrets Act (DTSA)**
- **California Uniform Trade Secrets Act (CUTSA)**

All employees and partners must sign NDAs explicitly covering these items.

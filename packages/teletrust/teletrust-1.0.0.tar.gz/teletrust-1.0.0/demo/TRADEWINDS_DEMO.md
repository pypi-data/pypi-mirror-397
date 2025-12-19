# TeleTrust Demo for DoD CDAO Tradewinds

## Quick Start (One-Click Demo)

```powershell
# From project root:
.\demo\run_tradewinds_demo.ps1
```

This launches all demos simultaneously for recording your Video Solution Brief.

---

## Demo Components for VSB

### 1. Compliance Gateway API (Core Product)

**Port:** 8000
**URL:** <http://localhost:8000/docs>
**Shows:** Real-time compliance checking with audit logs

```bash
curl -X POST http://localhost:8000/govern \
  -H "Authorization: Bearer sk_demo_public" \
  -H "Content-Type: application/json" \
  -d '{"action": "prescribe_medication", "context": "telehealth_session"}'
```

### 2. Pre-Bill Claim Scrubber (Healthcare Focus)

**Port:** 8501
**URL:** <http://localhost:8501>
**Shows:** CSV upload → auto-correction → denial prevention

### 3. ESM Rhythm Engine Metrics (91% Efficacy)

**Port:** 8502
**URL:** <http://localhost:8502>
**Shows:** Real-time anomaly detection with spectral visualization

---

## Recording Your 5-Minute VSB

### Script Outline

| Time | Segment | Demo |
|------|---------|------|
| 0:00-0:30 | **Hook** | "Commercial AI hallucinates. We don't." |
| 0:30-1:30 | **Problem** | Show AI failure examples, cost of non-compliance |
| 1:30-3:00 | **Solution** | Live API demo: compliance check in milliseconds |
| 3:00-4:00 | **Proof** | Show 91% efficacy metrics, 0% data retention |
| 4:00-4:30 | **Use Cases** | DoD AI Scaffolding, Healthcare, Finance |
| 4:30-5:00 | **CTA** | "Ready for Awardable evaluation" |

### Key Talking Points

1. **91% Anomaly Detection Rate** - Proven on real healthcare data
2. **0% Data Retention** - Ephemeral processing, HIPAA/DoD compliant
3. **61-Node Spectral Graph** - Not a simple filter, stateful safety
4. **Fail-Closed Design** - Blocks unsafe outputs, never lets them through

---

## Sample Test Data

Use `demo/sample_claims.csv` for the Pre-Bill Scrubber demo:

```csv
claim_id,patient_state,provider_state,pos,cpt
CLM001,CA,CA,02,99213
CLM002,CA,NV,11,99214
CLM003,TX,TX,10,90837
```

---

## Recording Tips

1. Use OBS Studio or Windows Game Bar (Win+G)
2. Record at 1080p, 30fps minimum
3. Speak clearly, use screen zoom for API responses
4. Show the audit log being generated in real-time

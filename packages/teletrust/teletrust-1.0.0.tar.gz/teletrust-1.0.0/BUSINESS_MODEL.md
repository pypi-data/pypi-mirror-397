# TeleTrust Business Model & Pricing Tiers

## Revenue Streams

### 1. API Metered Billing (Primary)

Per-compliance-check pricing via Stripe metered billing.

| Tier | Price/Check | Volume | Target Customer |
|------|-------------|--------|-----------------|
| Starter | $0.50 | 0-1,000/mo | Solo PMHNPs, small clinics |
| Pro | $0.25 | 1,001-10,000/mo | Mid-size telehealth platforms |
| Enterprise | $0.10 | 10,001+/mo | Hospital systems, EHR vendors |

### 2. Subscription Tiers

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0/mo | 100 checks, community support, watermarked logs |
| **Starter** | $49/mo | 1,000 checks, email support, full audit logs |
| **Pro** | $199/mo | 5,000 checks, priority support, custom rules |
| **Enterprise** | Custom | Unlimited, SLA, on-prem option, dedicated CSM |

### 3. OEM/White-Label Licensing

| License Type | Price | Use Case |
|--------------|-------|----------|
| Embedded API | $5,000/yr + usage | SaaS platforms embedding compliance |
| Source License | $50,000 one-time | On-prem deployment, no API dependency |
| ESM Core License | $100,000+/yr | Hallucination detection for enterprise AI |

---

## Unit Economics

| Metric | Value |
|--------|-------|
| LLM API cost per check | ~$0.02 (GPT-3.5) |
| Stripe fee per $10 | ~$0.60 |
| Gross margin (Starter) | ~92% |
| Break-even customers | 50 @ Pro tier |

---

## MRR Projections

| Month | Customers | Avg MRR/Customer | Total MRR |
|-------|-----------|------------------|-----------|
| 1 | 5 | $99 | $495 |
| 3 | 25 | $149 | $3,725 |
| 6 | 100 | $199 | $19,900 |
| 12 | 300 | $249 | $74,700 |

---

## Go-To-Market Channels

1. **Direct Sales**: Cold outreach to compliance officers (3-email sequence)
2. **Marketplaces**: PyPI, GitHub Sponsors, Azure/GCP Marketplace
3. **Partnerships**: EHR vendors, telehealth platforms
4. **Content**: Technical blog, compliance guides, whitepapers

---

## Competitive Moat

| Asset | Protection |
|-------|------------|
| ESM Rhythm Engine | Patent claims + trade secrets |
| Calibration constants | Trade secret (never published) |
| 61-node topology | Trade secret |
| PHI detection heuristics | Trade secret |
| Audit ledger HMAC | Production secret |

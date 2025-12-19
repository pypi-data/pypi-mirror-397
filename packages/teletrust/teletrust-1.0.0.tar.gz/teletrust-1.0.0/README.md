# MOA Telehealth Governor

**Multi-agent Orchestration Architecture for Healthcare Compliance**

**Owner:** Michael Ordon
**Version:** 2.0.0 (Rhythm Enhancement)
**Status:** PROPRIETARY — DO NOT DISTRIBUTE

---

## Quick Start

```bash
# Backend (FastAPI)
cd moa_telehealth_governor
pip install -r requirements.txt
python run_demo.py

# Frontend (React + Vite)
cd client
npm install
npm run dev  # http://localhost:5173
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOA TELEHEALTH GOVERNOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐         │
│  │  React   │───►│   FastAPI    │───►│ TelehealthGov │         │
│  │   UI     │    │   /govern    │    │   Governor    │         │
│  └──────────┘    └──────────────┘    └───────┬───────┘         │
│                                              │                  │
│       ┌──────────────────────────────────────┼──────────┐      │
│       ▼                  ▼                   ▼          ▼      │
│  ┌──────────┐    ┌──────────────┐    ┌──────────┐  ┌────────┐ │
│  │   ESM    │    │   Rhythm     │    │   Moa    │  │ Stripe │ │
│  │Compressor│    │   Tracker    │    │  Router  │  │Billing │ │
│  └──────────┘    └──────────────┘    └──────────┘  └────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### `/src/governor/telehealth_governor.py`

Main orchestrator. Processes user input, routes by risk zone (GREEN/YELLOW/RED).

### `/src/physics/esm_compressor.py`

FFT-based spectral analysis. Computes entropy for bot/human detection.

### `/src/physics/rhythm_dynamics.py` ⭐ NEW

Adaptive α (forgetting rate) per spectral mode. Trade secret.

### `/src/routing/moa_router.py`

Zone-based model routing. GREEN → Ollama (local), YELLOW → Cloud, RED → Frontier + human.

### `/src/billing/stripe_integration.py`

Payment processing. Ready for metered billing.

### `/client/`

React + shadcn/ui frontend. Vite dev server with proxy to FastAPI.

---

## Key IP (Trade Secrets)

| Component | Value | Protection |
|-----------|-------|------------|
| 61-node graph topology | $50-100K | Never open-source |
| Rhythm dynamics (adaptive α) | $100K+ | Proprietary |
| Prime Gödel codes (343 states) | $75K | Patent pending |
| Event-to-injection mappings | $75-150K/vertical | Licensed separately |

---

## Tier Structure

| Tier | Price | Includes |
|------|-------|----------|
| **OPEN** | Free | Theory, basic examples |
| **PRO** | $49-299/mo | Healthcare events, rhythm |
| **ENTERPRISE** | $2,499+/mo | Custom calibration, SLA |

---

## Tests

```bash
python run_demo.py           # 3 scenarios
python run_full_demo.py      # 67% token savings demo
python tests/verify_esm_physics.py
```

---

## Audit Checklist

- [ ] Verify spectral entropy calculation (`esm_compressor.py`)
- [ ] Check rhythm dynamics α bounds (0.01-0.15)
- [ ] Validate Prime Gödel bijection (343 unique codes)
- [ ] Confirm zone routing logic (GREEN/YELLOW/RED)
- [ ] Review crisis keyword detection (`mcp_interceptor.py`)
- [ ] Test Ollama fallback in `moa_router.py`

---

## Files to Review

```
src/
├── governor/telehealth_governor.py  # Main orchestrator
├── physics/
│   ├── esm_compressor.py            # FFT + entropy
│   ├── rhythm_dynamics.py           # Adaptive α
│   └── prime_codecs.py              # Gödel encoding
├── routing/moa_router.py            # Model tier routing
├── governance/mcp_interceptor.py    # Regulatory checks
└── billing/stripe_integration.py    # Payments

config/
├── router_config.yaml               # Model providers
└── thresholds.yaml                  # Risk thresholds

client/                              # React UI
tests/                               # Verification scripts
```

---

## Known Issues

1. `verify_esm_physics.py` — CHAOS/HUMAN thresholds need recalibration
2. TypeScript lint errors in client (tsconfig paths)
3. Ollama may timeout on first model load (30s)

---

## Contact

Michael Ordon — <grzywajk@gmail.com>

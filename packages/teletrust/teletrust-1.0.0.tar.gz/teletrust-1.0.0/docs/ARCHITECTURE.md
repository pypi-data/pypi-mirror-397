# MOA System Architecture & Workflow

## Global Mind Map

```
                              ┌──────────────────────────────────────┐
                              │        MOA TELEHEALTH GOVERNOR       │
                              │         "AI Governance Layer"        │
                              └──────────────────┬───────────────────┘
                                                 │
              ┌──────────────────────────────────┼──────────────────────────────────┐
              │                                  │                                  │
              ▼                                  ▼                                  ▼
     ┌────────────────┐                ┌────────────────┐                ┌────────────────┐
     │   CORE ENGINE  │                │   COMMERCIAL   │                │   AUTOMATION   │
     └───────┬────────┘                └───────┬────────┘                └───────┬────────┘
             │                                 │                                 │
    ┌────────┴────────┐               ┌────────┴────────┐               ┌────────┴────────┐
    │                 │               │                 │               │                 │
    ▼                 ▼               ▼                 ▼               ▼                 ▼
┌────────┐      ┌──────────┐    ┌────────┐      ┌────────┐      ┌────────┐      ┌────────┐
│Rhythm  │      │Citation  │    │Stripe  │      │Landing │      │n8n     │      │Ollama  │
│Engine  │      │Gateway   │    │Billing │      │Page    │      │Flows   │      │Guard   │
└────────┘      └──────────┘    └────────┘      └────────┘      └────────┘      └────────┘
    │                 │               │                │               │               │
    ▼                 ▼               ▼                ▼               ▼               ▼
 IP Core         Regulatory       Revenue          Acquisition      Lead Gen      Safety
 (Trade           Lookup           Pipeline          Funnel          Pipeline       Layer
  Secret)         (APIs)          (Webhooks)       (Conversion)     (Outreach)   (Guardrails)
```

---

## Production Stack (Battle-Tested OSS)

### Core Infrastructure

| Layer | Tool | Stars | Why |
|-------|------|-------|-----|
| **API Framework** | [FastAPI](https://github.com/tiangolo/fastapi) | 77k+ | Async, OpenAPI, production-ready |
| **Task Queue** | [Celery](https://github.com/celery/celery) | 24k+ | Distributed task processing |
| **Message Broker** | [Redis](https://github.com/redis/redis) | 66k+ | Fast, reliable pub/sub |
| **Database** | [PostgreSQL](https://github.com/postgres/postgres) | 16k+ | ACID, JSON support |
| **ORM** | [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy) | 9k+ | Industry standard |

### AI & LLM

| Layer | Tool | Stars | Why |
|-------|------|-------|-----|
| **Local LLM** | [Ollama](https://github.com/ollama/ollama) | 100k+ | Simple, fast, local |
| **Embeddings** | [sentence-transformers](https://github.com/UKPLab/sentence-transformers) | 15k+ | SOTA embeddings |
| **Vector DB** | [ChromaDB](https://github.com/chroma-core/chroma) | 15k+ | Simple, embedded |
| **Guardrails** | [guardrails-ai](https://github.com/guardrails-ai/guardrails) | 4k+ | LLM output validation |
| **Prompts** | [LangChain](https://github.com/langchain-ai/langchain) | 95k+ | Orchestration patterns |

### Security & Auth

| Layer | Tool | Stars | Why |
|-------|------|-------|-----|
| **Auth** | [Authlib](https://github.com/lepture/authlib) | 4k+ | OAuth2, JWT |
| **Secrets** | [python-dotenv](https://github.com/theskumar/python-dotenv) | 7k+ | Env management |
| **Encryption** | [cryptography](https://github.com/pyca/cryptography) | 6k+ | Industry standard |
| **API Keys** | [Unkey](https://github.com/unkeyed/unkey) | 3k+ | API key management |

### Automation & Workflows

| Layer | Tool | Stars | Why |
|-------|------|-------|-----|
| **Workflow Engine** | [n8n](https://github.com/n8n-io/n8n) | 47k+ | Open source Zapier |
| **Scheduling** | [APScheduler](https://github.com/agronholm/apscheduler) | 6k+ | Python scheduler |
| **Email** | [Resend](https://github.com/resend/resend-python) | 1k+ | Developer-first email |

### Observability

| Layer | Tool | Stars | Why |
|-------|------|-------|-----|
| **Logging** | [structlog](https://github.com/hynek/structlog) | 3k+ | Structured logging |
| **Metrics** | [prometheus-client](https://github.com/prometheus/client_python) | 4k+ | Industry standard |
| **Tracing** | [opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python) | 2k+ | CNCF standard |

---

## Workflow Diagrams

### 1. Lead → Customer Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   SOURCE    │────▶│   QUALIFY   │────▶│  OUTREACH   │────▶│  CONVERT    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
      │                   │                   │                   │
      ▼                   ▼                   ▼                   ▼
 LinkedIn API        Ollama Score         Email + Guard       Stripe Checkout
 Apollo.io           Company Size         Follow-up           Webhook
 HN/Reddit           Tech Stack           Demo Call           Provision
```

### 2. Request → Response (Governed)

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Request  │───▶│ PHI      │───▶│ Rhythm   │───▶│ Citation │───▶│ Response │
│ Inbound  │    │ Guard    │    │ Engine   │    │ Gateway  │    │ + Audit  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                    │                │                │
                    ▼                ▼                ▼
                 BLOCK           State Track       Verify
                 if PHI          + Memory          Sources
```

### 3. Deploy → Monitor Pipeline

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Code    │───▶│   CI     │───▶│  Deploy  │───▶│  Health  │───▶│  Alert   │
│  Push    │    │  Tests   │    │  Fly.dev │    │  Check   │    │  Slack   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │               │
     ▼               ▼               ▼               ▼               ▼
  GitHub          Ruff/Pytest      Docker         /health         PagerDuty
  Actions         IP Guard         Build          Metrics         On-Call
```

---

## Implementation Guide

### Phase 1: Foundation (Week 1)

```bash
# Install production dependencies
pip install fastapi uvicorn sqlalchemy redis celery \
            python-dotenv structlog prometheus-client \
            guardrails-ai chromadb

# Start Redis (message broker)
docker run -d --name redis -p 6379:6379 redis:alpine

# Start n8n (workflow automation)
docker run -d --name n8n -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n

# Start Ollama (local LLM)
ollama serve
ollama pull gemma2:2b
```

### Phase 2: Guardrails Integration (Week 2)

```python
# src/guards/llm_guard.py
from guardrails import Guard
from guardrails.hub import DetectPII, ToxicLanguage

guard = Guard().use_many(
    DetectPII(on_fail="exception"),
    ToxicLanguage(on_fail="exception")
)

def safe_generate(prompt: str) -> str:
    """Generate LLM output with guardrails."""
    result = guard(
        llm_api=ollama_generate,
        prompt=prompt,
    )
    return result.validated_output
```

### Phase 3: Automation Flows (Week 3)

```python
# src/automation/lead_pipeline.py
from celery import Celery
import structlog

app = Celery('moa', broker='redis://localhost:6379')
log = structlog.get_logger()

@app.task
def process_lead(lead_data: dict):
    """Process new lead through pipeline."""
    log.info("processing_lead", email=lead_data.get("email"))

    # 1. Enrich
    enriched = enrich_lead(lead_data)

    # 2. Score
    score = score_lead(enriched)

    # 3. Queue outreach if qualified
    if score > 0.7:
        queue_outreach.delay(enriched)

    return {"status": "processed", "score": score}

@app.task
def queue_outreach(lead: dict):
    """Generate and guard outreach message."""
    message = generate_outreach(lead)

    # Guardrail check
    check = pre_send_check(message)
    if not check["safe"]:
        log.warning("outreach_blocked", issues=check["issues"])
        return {"status": "blocked", "issues": check["issues"]}

    # Send via Resend
    send_email(lead["email"], message)
    return {"status": "sent"}
```

---

## Project Structure (Professional)

```
moa_telehealth_governor/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app
│   │   ├── routes/
│   │   │   ├── govern.py       # /govern endpoint
│   │   │   ├── billing.py      # /subscribe, /webhooks
│   │   │   └── health.py       # /health, /metrics
│   │   └── middleware/
│   │       ├── auth.py         # API key validation
│   │       └── logging.py      # Request logging
│   ├── core/
│   │   ├── rhythm_engine.py    # PROPRIETARY - IP Core
│   │   ├── citation_gateway.py # Regulatory lookup
│   │   └── phi_guard.py        # PHI detection
│   ├── billing/
│   │   ├── stripe_integration.py
│   │   └── entitlements.py
│   ├── automation/
│   │   ├── lead_pipeline.py    # Lead processing
│   │   ├── outreach.py         # Email generation
│   │   └── guards.py           # Pre-send checks
│   └── models/
│       ├── database.py         # SQLAlchemy models
│       └── schemas.py          # Pydantic schemas
├── tests/
│   ├── test_api.py
│   ├── test_rhythm.py
│   └── test_guards.py
├── docs/
│   ├── WHITEPAPER.md
│   ├── FUNDING_GUIDE.md
│   └── AUTOMATION_GUIDE.md
├── .github/
│   └── workflows/
│       ├── ci.yml              # Tests + lint
│       └── deploy.yml          # Fly.dev deploy
├── docker-compose.yml
├── Dockerfile
├── fly.toml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Docker Compose (Full Stack)

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://moa:moa@db:5432/moa
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - redis
      - db

  worker:
    build: .
    command: celery -A src.automation.lead_pipeline worker -l info
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: moa
      POSTGRES_PASSWORD: moa
      POSTGRES_DB: moa
    volumes:
      - pgdata:/var/lib/postgresql/data

  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}

volumes:
  pgdata:
  n8n_data:
```

---

## Quick Commands

```powershell
# Start full stack locally
docker-compose up -d

# View logs
docker-compose logs -f api

# Run tests
pytest tests/ -v

# Deploy to Fly.dev
fly deploy

# Check production health
curl https://moa-telehealth-governor.fly.dev/health
```

---

## Status Checklist

- [x] Core API deployed (Fly.dev)
- [x] Stripe integration (webhooks working)
- [x] IP protection (trade secrets guarded)
- [x] Documentation (whitepaper, funding guide)
- [x] Delete dead Stripe webhook ✓ (marked done)
- [ ] n8n workflows configured
- [ ] Celery workers deployed
- [ ] Lead pipeline active
- [ ] First pilot acquired

---

## Next Action

```
1. Run: docker-compose up -d
2. Configure n8n at http://localhost:5678
3. Import lead workflow
4. Start outreach
```

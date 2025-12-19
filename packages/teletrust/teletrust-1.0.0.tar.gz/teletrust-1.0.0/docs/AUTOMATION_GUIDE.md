# MOA Sales & Community Automation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMATION PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Lead Sources]                                                 │
│   LinkedIn → n8n → Lead Enrichment → CRM                       │
│   HackerNews → Webhook → Qualify → Outreach Queue              │
│                                                                 │
│  [Outreach Engine]                                              │
│   Template + Context → Ollama Guard → Send/Queue                │
│                                                                 │
│  [Community Engagement]                                         │
│   Mentions → Sentiment → Draft Reply → Human Review → Post      │
│                                                                 │
│  [Email Response]                                               │
│   Inbound → Classify → Draft → Guard → Send/Escalate           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. n8n Workflow Setup

### 1.1 Installation (Docker)

```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_SECURE_COOKIE=false \
  n8nio/n8n
```

Access at: `http://localhost:5678`

### 1.2 Lead Generation Workflow

```json
{
  "name": "LinkedIn Lead Finder",
  "nodes": [
    {
      "type": "n8n-nodes-base.scheduleTrigger",
      "params": { "rule": { "interval": [{ "field": "hours", "hours": 24 }] } }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "params": {
        "url": "https://api.apollo.io/v1/mixed_people/search",
        "headers": { "Api-Key": "{{$env.APOLLO_API_KEY}}" },
        "body": {
          "person_titles": ["Compliance Officer", "Healthcare IT Manager", "Telehealth Director"],
          "person_locations": ["United States"],
          "organization_num_employees_ranges": ["1,10", "11,50"]
        }
      }
    },
    {
      "type": "n8n-nodes-base.function",
      "params": {
        "code": "// Filter and enrich leads\nreturn items.filter(i => i.json.email).map(i => ({ json: { name: i.json.name, email: i.json.email, company: i.json.organization_name, title: i.json.title } }));"
      }
    },
    {
      "type": "n8n-nodes-base.googleSheets",
      "params": {
        "operation": "append",
        "sheetId": "{{$env.LEADS_SHEET_ID}}",
        "range": "Leads!A:E"
      }
    }
  ]
}
```

---

## 2. Ollama Guardrail Integration

### 2.1 Local Ollama Setup

```powershell
# Ensure Ollama is running
ollama serve

# Pull guard model
ollama pull gemma2:2b
```

### 2.2 Guard Function (Python)

```python
# scripts/ollama_guard.py
import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def guard_outreach(message: str, context: dict) -> dict:
    """
    Check outreach message for:
    - No PII leaks
    - No trade secret exposure
    - Professional tone
    - Accurate claims only
    """
    prompt = f"""You are a compliance checker. Analyze this outreach message:

MESSAGE:
{message}

CONTEXT:
Sender: Michael Ordon
Company: MOA Telehealth Governor
Product: AI governance for healthcare

CHECK FOR:
1. Does it leak any API keys, passwords, or internal paths?
2. Does it mention trade secrets (rhythm_dynamics, beta=1.5, gamma=0.1)?
3. Is the tone professional?
4. Are all claims factual and verifiable?

Respond with JSON:
{{"safe": true/false, "issues": ["issue1", "issue2"], "suggestion": "..."}}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "gemma2:2b",
        "prompt": prompt,
        "stream": False
    })

    result = response.json().get("response", "{}")
    try:
        return json.loads(result)
    except:
        return {"safe": False, "issues": ["Parse error"], "suggestion": "Review manually"}


def guard_email_reply(inbound: str, draft_reply: str) -> dict:
    """Guard email replies before sending."""
    prompt = f"""You are an email compliance checker.

INBOUND EMAIL:
{inbound}

DRAFT REPLY:
{draft_reply}

CHECK:
1. Does reply address the sender's question?
2. No PII or trade secrets?
3. Professional tone?
4. No over-promises (e.g., "guaranteed 100% uptime")?

Respond with JSON:
{{"safe": true/false, "issues": [], "improved_reply": "..."}}
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "gemma2:2b",
        "prompt": prompt,
        "stream": False
    })

    return json.loads(response.json().get("response", '{"safe": false}'))
```

---

## 3. Email Templates (Protected)

### 3.1 Template: Initial Outreach

```python
# scripts/email_templates.py
TEMPLATES = {
    "initial_outreach": {
        "subject": "Quick question about {company} telehealth compliance",
        "body": """Hi {first_name},

I noticed you're {title} at {company}. Quick question:

How much time does your team spend on compliance documentation per telehealth visit?

I built MOA Governor specifically for this — it validates consent, checks state-specific rules (like CA AB-688), and generates audit-ready evidence packs automatically.

Would you be open to a 15-minute demo? I can show you how it works with real examples.

Best,
Michael Ordon
grzywajk@gmail.com

P.S. Here's a quick demo: https://moa-telehealth-governor.fly.dev/health
""",
        "guardrails": ["no_pii", "no_trade_secrets", "professional_tone"]
    },

    "follow_up": {
        "subject": "Re: {company} telehealth compliance",
        "body": """Hi {first_name},

Just wanted to follow up on my note last week.

We recently helped a PMHNP practice reduce their compliance documentation time by 80%. Happy to share details if useful.

Best,
Michael
""",
        "guardrails": ["no_pii", "no_false_claims"]
    }
}
```

---

## 4. Community Engagement Automation

### 4.1 Reddit/HN Monitor (n8n Workflow)

```json
{
  "name": "Community Monitor",
  "nodes": [
    {
      "type": "n8n-nodes-base.rssFeed",
      "params": {
        "url": "https://hnrss.org/newest?q=telehealth+compliance"
      }
    },
    {
      "type": "n8n-nodes-base.httpRequest",
      "note": "Call Ollama to draft reply",
      "params": {
        "url": "http://localhost:11434/api/generate",
        "method": "POST",
        "body": {
          "model": "gemma2:2b",
          "prompt": "Draft a helpful, non-promotional reply to this HN post: {{$json.title}}. Focus on being genuinely helpful. Do not mention MOA directly unless it solves a specific problem mentioned.",
          "stream": false
        }
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "note": "Send to #community-review for human approval",
      "params": {
        "channel": "#community-review",
        "text": "New HN mention:\n{{$json.title}}\n\nDraft reply:\n{{$json.draft}}\n\nApprove? React with ✅ to post."
      }
    }
  ]
}
```

---

## 5. Sanity Checks & Validation

### 5.1 Pre-Send Checklist (Automated)

```python
# scripts/pre_send_check.py
import re

BLOCKED_PATTERNS = [
    r"sk_live_[A-Za-z0-9]+",      # Stripe secret key
    r"whsec_[A-Za-z0-9]+",        # Webhook secret
    r"beta\s*=\s*1\.5",           # Trade secret param
    r"gamma\s*=\s*0\.1",          # Trade secret param
    r"rhythm_dynamics",           # IP marker
    r"61-node",                   # IP marker
    r"MrMidas",                   # Password fragment
]

def pre_send_check(content: str) -> dict:
    """Run sanity checks before any external communication."""
    issues = []

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(f"BLOCKED: Pattern '{pattern}' found")

    # Check for excessive claims
    if "100%" in content and "uptime" in content.lower():
        issues.append("WARNING: Avoid '100% uptime' claims")

    if "guaranteed" in content.lower():
        issues.append("WARNING: Avoid 'guaranteed' without qualification")

    return {
        "safe": len(issues) == 0,
        "issues": issues,
        "reviewed_at": datetime.now().isoformat()
    }
```

---

## 6. Login & Credential Manager

### 6.1 Secure Config (DO NOT COMMIT)

```json
// M:\Projects\Launchpad\automation_secrets.json (gitignored)
{
  "email": {
    "address": "grzywajk@gmail.com",
    "app_password": "REDACTED"
  },
  "linkedin": {
    "username": "michael-ordon",
    "session_cookie": "REDACTED"
  },
  "apollo": {
    "api_key": "REDACTED"
  },
  "n8n": {
    "webhook_secret": "REDACTED"
  },
  "ollama": {
    "url": "http://localhost:11434"
  }
}
```

### 6.2 Load Secrets Helper

```python
# scripts/secrets_loader.py
import json
import os

SECRETS_PATH = os.environ.get("MOA_SECRETS_PATH", "M:/Projects/Launchpad/automation_secrets.json")

def load_secrets():
    with open(SECRETS_PATH) as f:
        return json.load(f)

def get_secret(key_path: str):
    """Get nested secret: 'email.address' -> secrets['email']['address']"""
    secrets = load_secrets()
    keys = key_path.split(".")
    value = secrets
    for k in keys:
        value = value[k]
    return value
```

---

## 7. Developer Docs Integration

### 7.1 RAG for Best Practices

```python
# scripts/docs_rag.py
import requests

DOCS_SOURCES = {
    "stripe": "https://docs.stripe.com/api",
    "fly": "https://fly.io/docs",
    "fastapi": "https://fastapi.tiangolo.com",
    "n8n": "https://docs.n8n.io"
}

def query_docs(question: str, source: str = "all") -> str:
    """Query developer docs via Ollama with context."""
    # In production, use embeddings + vector DB
    # For now, use Ollama with general knowledge

    prompt = f"""You are a technical assistant with knowledge of:
- Stripe API best practices
- Fly.io deployment patterns
- FastAPI security guidelines
- n8n workflow automation

Question: {question}

Answer with specific, actionable guidance. Cite documentation sections when possible.
"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma2:2b",
        "prompt": prompt,
        "stream": False
    })

    return response.json().get("response", "No response")
```

---

## 8. Quick Start Commands

```powershell
# Start n8n (Docker)
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n

# Ensure Ollama is running
ollama serve

# Test guard function
cd M:\source\repos\moa_telehealth_governor
python -c "from scripts.ollama_guard import guard_outreach; print(guard_outreach('Hello, want a demo?', {}))"

# Run pre-send check
python -c "from scripts.pre_send_check import pre_send_check; print(pre_send_check('Hello world'))"
```

---

## 9. Workflow Triggers

| Trigger | Action | Guard | Output |
|---------|--------|-------|--------|
| Daily 9am | Fetch new leads | None | Google Sheet |
| New lead added | Generate outreach | Ollama + Pattern | Draft queue |
| Draft approved | Send email | Pre-send check | Gmail |
| HN/Reddit mention | Draft reply | Ollama | Slack for review |
| Inbound email | Classify + draft | Ollama | Review queue |

---

## 10. IP Protection Rules (Hardcoded)

**NEVER include in any external communication:**

- `beta = 1.5`
- `gamma = 0.1`
- `a0 = 5.0`
- `61-node`
- `rhythm_dynamics`
- `Prime Gödelization`
- `spectral_engine`
- Any file paths containing `M:\source\`
- Any API keys or secrets

**Safe to mention:**
- "Adaptive memory retention"
- "Spectral governance"
- "+9.5% to +17.5% retention advantage"
- "Fail-closed architecture"
- "Audit-grade evidence"

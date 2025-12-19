from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import time
from datetime import datetime

# Ensure src is in path
sys.path.append(os.getcwd())

from src.governor.telehealth_governor import TelehealthGovernor

app = FastAPI(
    title="MOA Telehealth Governor API",
    version="1.0.0",
    description="AI Governance API for Telehealth Compliance with Zero-PHI Processing"
)

# Usage tracking (in-memory for MVP, use Redis/DB in production)
usage_ledger: Dict[str, Dict[str, Any]] = {}

# Initialize Governor Singleton
# In production, config might come from env vars
governor = TelehealthGovernor()

# Tier-0 Auth: Load from environment
# Format: "token:client_id,token2:client_id2"
_tokens_env = os.environ.get("MOA_API_TOKENS", "")
ALLOWED_TOKENS = {}
if _tokens_env:
    ALLOWED_TOKENS = dict(pair.split(":") for pair in _tokens_env.split(",") if ":" in pair)

class GovernRequest(BaseModel):
    session_id: str
    text: str
    context: Optional[Dict[str, Any]] = None # Added for Compliance Context


class GovernResponse(BaseModel):
    session_id: str
    risk_score: float
    zone: str
    output_text: str
    cost_usd: float
    action_log: List[str]
    prime_code_macro: int
    prime_code_nodes: str
    regulatory_signals: List[str]
    compliance_verdict: str
    billing: Optional[Dict[str, Any]] = None # Added v1.1
    required_actions: Optional[List[Dict[str, Any]]] = None # Added v1.1
    sanitization: Optional[Dict[str, Any]] = None # Added v1.1
    usage_events: Optional[List[Dict[str, Any]]] = None # Added v1.1
    evidence: Optional[List[Dict[str, Any]]] = None # Added v1.1

async def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
             raise HTTPException(status_code=401, detail="Invalid Authentication Scheme")

        if token not in ALLOWED_TOKENS:
             raise HTTPException(status_code=401, detail="Invalid API Token")

        return ALLOWED_TOKENS[token] # Return client_id
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Authorization Header Format")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "moa-telehealth-governor",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/pricing")
def get_pricing():
    """Return pricing tiers for the API."""
    return {
        "tiers": {
            "basic": {
                "name": "Basic",
                "price_monthly": 299,
                "requests_per_month": 1000,
                "features": ["Compliance validation", "Basic audit trail", "Email support"]
            },
            "pro": {
                "name": "Pro",
                "price_monthly": 599,
                "requests_per_month": 5000,
                "features": ["All Basic features", "Real-time regulatory checks", "Priority support", "API webhook callbacks"]
            },
            "enterprise": {
                "name": "Enterprise",
                "price_monthly": 999,
                "requests_per_month": "unlimited",
                "features": ["All Pro features", "Custom compliance rules", "Dedicated support", "SLA guarantee", "On-premise option"]
            }
        },
        "metered_pricing": {
            "per_request": 0.01,
            "per_1000_tokens": 0.005
        }
    }

@app.get("/usage")
def get_usage(client_id: str = Depends(verify_token)):
    """Get usage statistics for the authenticated client."""
    client_usage = usage_ledger.get(client_id, {
        "total_requests": 0,
        "total_cost_usd": 0.0,
        "requests_by_zone": {},
        "last_request": None
    })
    return {
        "client_id": client_id,
        "period": "current_month",
        "usage": client_usage
    }

@app.post("/govern", response_model=GovernResponse)
def govern_interaction(req: GovernRequest, client_id: str = Depends(verify_token)):
    """
    Main entry point for Governed AI.
    1. Validates API Token.
    2. Passes text to TelehealthGovernor (Physics -> Gate -> Router).
    3. Records usage for billing.
    4. Returns audit trail and response.
    """
    start_time = time.time()

    try:
        result = governor.process_interaction(req.session_id, req.text, context=req.context)

        # Track usage for billing
        if client_id not in usage_ledger:
            usage_ledger[client_id] = {
                "total_requests": 0,
                "total_cost_usd": 0.0,
                "requests_by_zone": {},
                "last_request": None
            }

        usage_ledger[client_id]["total_requests"] += 1
        usage_ledger[client_id]["total_cost_usd"] += result.cost_usd
        usage_ledger[client_id]["requests_by_zone"][result.zone] = \
            usage_ledger[client_id]["requests_by_zone"].get(result.zone, 0) + 1
        usage_ledger[client_id]["last_request"] = datetime.utcnow().isoformat()

        latency_ms = (time.time() - start_time) * 1000
        print(f"[BILLING] Client: {client_id} | Cost: ${result.cost_usd:.4f} | Zone: {result.zone} | Latency: {latency_ms:.1f}ms")

        return GovernResponse(
            session_id=result.session_id,
            risk_score=result.risk_score,
            zone=result.zone,
            output_text=result.output_text,
            cost_usd=result.cost_usd,
            action_log=result.action_log,
            prime_code_macro=result.prime_code_macro,
            prime_code_nodes=result.prime_code_nodes,
            regulatory_signals=result.regulatory_signals or [],
            compliance_verdict=result.compliance_verdict,
            billing=result.billing,
            required_actions=result.required_actions,
            sanitization=result.sanitization,
            usage_events=result.usage_events,
            evidence=result.evidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

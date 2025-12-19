"""
MoaRouter
---------
Routes work to the appropriate model tier (local/mid/frontier) and
executes real LLM calls if configured.

Tiers:
  - GREEN / Local: Stubbed (simulates Llama-3-8b via vLLM)
  - YELLOW / Mid: GPT-4o-mini (via OpenAI)
  - RED / Frontier: GPT-4o (via OpenAI)
"""

from __future__ import annotations
import os
import time
from typing import Any, Dict

# Load environment variables from config/secrets/.env if present
try:
    from dotenv import load_dotenv
    load_dotenv("config/secrets/.env")
except ImportError:
    pass

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("Warning: 'openai' package not found. Using stubs.")

class MoaRouter:
  def __init__(self, config: Dict[str, Any] | None = None) -> None:
      cfg = config or {}
      self.models = cfg.get("models", {
          "local": "llama-3-8b",
          "mid": "gpt-4o-mini",
          "frontier": "gpt-4o"
      })
      self.costs = cfg.get("cost_estimates_usd", {
          "local_per_1k": 0.0,
          "mid_per_1k": 0.00015,   # $0.15 / 1M input tokens (approx)
          "frontier_per_1k": 0.005 # $5.00 / 1M input tokens (approx)
      })

      # Initialize OpenAI Client
      self.client = None
      if HAS_OPENAI and os.getenv("OPENAI_API_KEY"):
          self.client = OpenAI()
      elif HAS_OPENAI:
          print("Warning: OPENAI_API_KEY not found in environment. Using stubs.")

  def route_and_execute(self, user_input: str, state: Dict[str, Any], zone: str) -> Dict[str, Any]:
      # 1. Determine Tier
      if zone == "GREEN":
          tier = "local"
      elif zone == "YELLOW":
          tier = "mid"
      else:
          tier = "frontier"

      model = self.models.get(tier, "unknown-model")

      # 2. Execute
      t0 = time.time()

      # LOCAL TIER (Always stubbed for MVP logic until vLLM is connected)
      if tier == "local":
           content = f"[{tier.upper()}:{model}] (Local Simulation) Safe to process locally. {user_input[:50]}..."
           usage_tokens = len(user_input.split())  # Estimate

      # CLOUD TIERS (Real Calls)
      elif self.client and (tier == "mid" or tier == "frontier"):
          try:
              completion = self.client.chat.completions.create(
                  model=model,
                  messages=[
                      {"role": "system", "content": "You are a helpful telehealth assistant."},
                      {"role": "user", "content": user_input}
                  ]
              )
              content = completion.choices[0].message.content
              usage_tokens = completion.usage.total_tokens
          except Exception as e:
              content = f"[{tier.upper()}:{model}] API Error: {str(e)}"
              usage_tokens = 0

      # FALLBACK STUB
      else:
           content = f"[{tier.upper()}:{model}] (Stub - Missing Key/Lib) {user_input[:50]}..."
           usage_tokens = len(user_input.split())

      # 3. Calculate Cost
      # Use simple "per_1k" based on total tokens (input + output approx)
      per_1k = self.costs.get(f"{tier}_per_1k", 0.0)
      cost = per_1k * (usage_tokens / 1000.0)

      return {
          "content": content,
          "cost": float(cost),
          "tier": tier,
          "model": model,
          "latency": time.time() - t0
      }

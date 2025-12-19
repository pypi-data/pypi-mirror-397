from __future__ import annotations
from typing import Any, Dict, List

class MoaTokenGate:
    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        self.config = config or {}
        # Deep merge/lookup could be better, but assuming structure for MVP
        gate_cfg = self.config.get("thresholds", {}).get("gate", {}) # Note: tier0_config passes 'gate' config which has 'thresholds'

        # Fallback to direct config if not nested
        if not gate_cfg:
             gate_cfg = self.config.get("thresholds", {}).get("gate", {})

        self.entropy_cfg = gate_cfg.get("entropy", {
            "standard_min": 3.0, "standard_max": 5.5,
            "critical_min": 2.0, "critical_max": 6.0
        })

        risk_cfg = self.config.get("thresholds", {}).get("risk", {})
        self.green_max = risk_cfg.get("green_max", 30)
        self.yellow_max = risk_cfg.get("yellow_max", 70)

    def evaluate(self, state: Dict[str, Any]) -> Dict[str, Any]:
        import math
        entropy = float(state.get("spectral_state", {}).get("entropy", 0.0))
        flags: List[str] = list(state.get("structural_tokens", {}).get("risk_flags", []))

        # P0: NaN/Inf Fail-Closed Guard
        if not math.isfinite(entropy):
            return {
                "risk_score": 100.0,
                "zone": "RED",
                "flags": ["CRITICAL_NAN_INF_DETECTED"],
                "action": "BLOCK",
            }

        # 1. Entropy Band Check
        score = 0.0

        # Chaotic / Bot checks
        if entropy < self.entropy_cfg["critical_min"]:
            flags.append("CRITICAL_BOT_DETECTED")
            score += 100.0
        elif entropy > self.entropy_cfg["critical_max"]:
             flags.append("CRITICAL_CHAOS_DETECTED")
             score += 100.0

        # Out of Distribution (OOD) checks
        elif entropy < self.entropy_cfg["standard_min"]:
             flags.append("LOW_ENTROPY_OOD")
             score += 50.0
        elif entropy > self.entropy_cfg["standard_max"]:
             flags.append("HIGH_ENTROPY_OOD")
             score += 50.0

        # 2. Flag Penalties
        # Existing flags from Physics (e.g. specific rail violations)
        score += 20.0 * len(flags)

        # 3. Zone Assignment
        base_risk = min(100.0, score)

        if base_risk <= self.green_max:
            zone = "GREEN"
        elif base_risk <= self.yellow_max:
            zone = "YELLOW"
        else:
            zone = "RED"

        decision = {
            "risk_score": base_risk,
            "zone": zone,
            "flags": flags,
            "action": "BLOCK" if zone == "RED" else "PASS",
        }
        return decision

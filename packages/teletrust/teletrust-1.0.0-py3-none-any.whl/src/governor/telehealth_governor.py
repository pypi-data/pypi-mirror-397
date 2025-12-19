from __future__ import annotations
import time
import hmac
import hashlib
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from src.physics.esm_compressor import ESMCompressor
from src.governance.moa_gate import MoaTokenGate
from src.routing.moa_router import MoaRouter
from src.governance.audit_logger import AuditLogger
from src.tools.phi_guard import PhiGuard
from src.compliance.engine import ComplianceEngine

from src.billing.moa_usage_ledger import MoaUsageLedger
from src.billing.payment_guard import PaymentGuard


@dataclass
class GovernanceResult:
    session_id: str
    input_text: str
    output_text: str
    risk_score: float
    zone: str
    cost_usd: float
    action_log: List[str]
    pattern_id: str = "unknown"
    regulatory_signals: List[str] = None
    compliance_verdict: str = "N/A"
    prime_code_macro: int = 0
    prime_code_nodes: str = "0x0"
    # Added v1.1 fields
    billing: Dict[str, Any] = None
    required_actions: List[Dict[str, Any]] = None
    sanitization: Dict[str, Any] = None
    usage_events: List[Dict[str, Any]] = None
    evidence: List[Dict[str, Any]] = None


class TelehealthGovernor:
    def __init__(self, config: Dict[str, Any] | None = None) -> None:
        cfg = config or {}
        # ... (previous init code)
        physics_cfg = cfg.get("physics", {})
        gate_cfg = cfg.get("gate", {})
        self.esm = ESMCompressor(physics_cfg)
        self.gate = MoaTokenGate(gate_cfg)
        self.compliance_engine = ComplianceEngine()
        self.router = MoaRouter(cfg.get("router"))
        self.logger = AuditLogger()
        self.phi_guard = PhiGuard()
        self.ledger = MoaUsageLedger()
        self.payment_guard = PaymentGuard()  # Initialize PaymentGuard
        self.session_states: Dict[str, Dict[str, Any]] = {}
        self.budgets = cfg.get("budgets", {"monthly_cap": 500.0, "current_spend": 0.0})
        self.step_counter = 0

    def _generate_hmac_receipt(self, content: str) -> str:
        """Generates a tamper-evident HMAC-SHA256 receipt for the content."""
        # In production, this key MUST come from a secure environment variable.
        # Fail-closed: default to empty string which will fail signature checks if key missing.
        secret_key = os.environ.get("MOA_AUDIT_HMAC_KEY_B64", "")
        mode = os.environ.get("MOA_MODE", "dev")
        
        if not secret_key:
            if mode == "prod":
                # PRO-GRADE: Fails immediately in production if key is missing
                raise RuntimeError("CRITICAL_SECURITY_ERROR: MOA_AUDIT_HMAC_KEY_B64 missing in PROD mode.")
            else:
                # Warning for dev environments
                print("[SECURITY_WARNING] Using default HMAC key. This IS NOT SECURE for production.")
                secret_key = "DEV_KEY_NON_PRODUCTION_FALLBACK"

        digest = hmac.new(
            secret_key.encode("utf-8"), content.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return digest

    def process_interaction(
        self, session_id: str, user_input: str, context: Dict[str, Any] = None
    ) -> GovernanceResult:
        t0 = time.time()
        logs: List[str] = []
        self.step_counter += 1

        # Security: Generate Receipt
        input_receipt = self._generate_hmac_receipt(user_input)
        logs.append(f"Audit Receipt: {input_receipt}")

        # Default context for compliance if not provided
        if context is None:
            context = {
                "patient_state": "FL",
                "provider_home_state": "NY",
                "service_mode": "video",
                "provider_type": "MD",
            }

        # Custom check for Payment Guard
        # In a real app, 'session_id' or 'context' would carry the customer token
        customer_token = context.get("customer_token", session_id) if context else session_id
        if not self.payment_guard.verify_subscription(customer_token):
            logs.append("BLOCK: Payment verification failed (Fail-Closed)")
            return GovernanceResult(
                session_id=session_id,
                input_text=user_input,
                output_text="Service Unavailable: Payment verification failed.",
                risk_score=1.0,
                zone="RED",
                cost_usd=0.0,
                action_log=logs,
                pattern_id="billing_block",
            )

        # 0. PHI Guard Check
        if self.phi_guard.scan(user_input):
            logs.append("PHI DETECTED")
            redacted_input = self.phi_guard.redact(user_input)
            logs.append(f"Input redacted: {redacted_input}")
            return GovernanceResult(
                session_id=session_id,
                input_text=user_input,
                output_text="I detected secure health information (PHI) in your message. To protect patient privacy, I cannot process this input.",
                risk_score=0.9,
                zone="RED",
                cost_usd=0.0,
                action_log=logs,
                pattern_id="phi_blocked",
            )

        # 1. Compliance Engine Check
        comp_res = self.compliance_engine.evaluate(context)
        logs.append(f"Compliance Verdict: {comp_res.verdict}")

        # Record Usage Events to Ledger (and populate result)
        for event in comp_res.usage_events:
            self.ledger.record_event(
                event_name=event["event"],
                quantity=event.get("quantity", 1),
                metadata={"verdict": comp_res.verdict, "tag": event.get("tag")},
            )
            logs.append(f"Ledger: Recorded {event['event']}")

        common_result_args = {
            "session_id": session_id,
            "input_text": user_input,
            "action_log": logs,
            "regulatory_signals": [e["title"] for e in comp_res.evidence],
            "compliance_verdict": comp_res.verdict,
            "billing": comp_res.billing,
            "required_actions": comp_res.required_actions,
            "sanitization": comp_res.sanitization,
            "usage_events": comp_res.usage_events,
            "evidence": comp_res.evidence,
        }

        if comp_res.verdict == "DENY":
            logs.append(f"Regulatory Block: {comp_res.reason}")
            # Log evidence for audit
            for ev in comp_res.evidence:
                logs.append(f"Cited: {ev.get('title')} ({ev.get('pin')})")

            return GovernanceResult(
                output_text=f"Blocked by Telehealth Compliance Engine: {comp_res.reason}",
                risk_score=1.0,
                zone="RED",
                cost_usd=0.0,
                pattern_id="regulatory_block",
                **common_result_args,
            )

        if comp_res.verdict == "CONDITIONAL":
            logs.append("Proceeding with conditions (Attestations Required).")

        # 1b. Crisis Escalation Path
        if "suicide" in user_input.lower():
            logs.append("CRISIS DETECTED - Immediate escalation required")
            return GovernanceResult(
                output_text="I'm concerned about what you've shared. Please reach out to the 988 Suicide & Crisis Lifeline (call or text 988).",
                risk_score=100.0,
                zone="RED",
                cost_usd=0.0,
                pattern_id="crisis_intervention",
                **common_result_args,
            )

        # 2. ESM Update
        state = self.session_states.get(session_id, self.esm.init_state())
        state = self.esm.update_state(state, user_input)

        # --- PRIME GÖDEL CODING LAYER ---
        entropy = state.get("spectral_state", {}).get("entropy", 0.0)
        logs.append(f"ESM updated. Entropy={entropy:.2f}")

        # Map entropy to bin 0-6
        if entropy < 2.0:
            e_bin = 0
        elif entropy < 3.0:
            e_bin = 1
        elif entropy < 3.2:
            e_bin = 2
        elif entropy < 4.0:
            e_bin = 3
        elif entropy < 5.1:
            e_bin = 4
        elif entropy < 6.0:
            e_bin = 5
        else:
            e_bin = 6

        macro_bins = (3, e_bin, 0)

        # Generate Node Mask
        node_mask = [False] * 61
        for i in range(21):
            node_mask[i] = True
        h = hash(user_input)
        for i in range(21, 61):
            if (h >> (i - 21)) & 1:
                node_mask[i] = True

        audit_entry = self.logger.log_state(
            step=self.step_counter,
            macro_bins=macro_bins,
            node_mask=node_mask,
            metadata={"session_hash": hash(session_id)},
        )

        state["prime_codes"] = {
            "macro": audit_entry["macro_code"],
            "nodes": int(audit_entry["node_code_hex"], 16),
        }
        self.session_states[session_id] = state
        # --------------------------------

        decision = self.gate.evaluate(state)
        risk = decision["risk_score"]
        zone = decision["zone"]
        logs.append(f"Gate decision: zone={zone}, risk={risk:.1f}")

        if decision.get("action") == "BLOCK":
            logs.append("Request blocked by policy.")
            return GovernanceResult(
                output_text="I cannot process this request due to safety policies.",
                risk_score=risk,
                zone=zone,
                cost_usd=0.0,
                prime_code_macro=state["prime_codes"]["macro"],
                prime_code_nodes=audit_entry["node_code_hex"],
                **common_result_args,
            )

        if not self._check_budget(zone):
            logs.append("Budget envelope exceeded. Downgrading to GREEN/local.")
            zone = "GREEN"

        routed = self.router.route_and_execute(user_input, state, zone)
        cost = float(routed["cost"])
        self._update_spend(cost)

        logs.append(f"Routed to tier={routed['tier']} model={routed['model']} cost=${cost:.4f}")
        latency = time.time() - t0
        logs.append(f"Latency={latency:.3f}s")
        logs.append(f"Audit: MacroCode={audit_entry['macro_code']}")

        # --- TRANSPARENCY LAYER (AB 489) ---
        final_output = self._apply_transparency_layer(routed["content"], context)
        # -----------------------------------

        return GovernanceResult(
            output_text=final_output,
            risk_score=risk,
            zone=zone,
            cost_usd=cost,
            prime_code_macro=state["prime_codes"]["macro"],
            prime_code_nodes=audit_entry["node_code_hex"],
            **common_result_args,
        )

    def _apply_transparency_layer(self, content: str, context: Dict[str, Any]) -> str:
        """
        Applies AB 489 (California) transparency requirements.
        Appends a clear disclosure that the content is AI-generated.
        """
        # Check if context implies California jurisdiction or default to safe
        patient_state = context.get("patient_state", "")
        provider_state = context.get("provider_home_state", "")

        # Apply globally for safety/uniformity in this pilot, or strictly for CA
        apply_disclaimer = True

        if apply_disclaimer:
            disclaimer = (
                "\n\n[NOTICE: This content was generated by an AI system (Triad-MOA) "
                "and is NOT a substitute for professional medical advice. "
                "A licensed provider must review this output before use. "
                "This system is not a doctor.]"
            )
            return content + disclaimer
        return content

    def _check_budget(self, zone: str) -> bool:
        current = self.budgets.get("current_spend", 0.0)
        cap = self.budgets.get("monthly_cap", 0.0)
        return current < cap

    def _update_spend(self, cost: float) -> None:
        self.budgets["current_spend"] = self.budgets.get("current_spend", 0.0) + cost


if __name__ == "__main__":
    gov = TelehealthGovernor()
    res = gov.process_interaction("sess_demo", "Patient is upset about billing code 99213.")
    print("Zone:", res.zone)
    print("Risk:", res.risk_score)
    print("Output:", res.output_text)
    print("Log:", *res.action_log, sep="\n - ")

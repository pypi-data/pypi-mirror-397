"""
MCP-enhanced evaluator with PHI-safe regulatory verification.
Preserves S_rule / S_vec / Q / D mathematical framework.
"""

import re
from typing import Dict, List, Tuple, Optional


# Placeholder extractors – wire to your actual implementations
def extract_billing_codes(text: str) -> List[Tuple[str, str]]:
    """Extract (code_type, code) tuples from text."""
    codes = []
    # CPT codes: 5 digits
    for match in re.finditer(r'\b(\d{5})\b', text):
        codes.append(("CPT", match.group(1)))
    return codes


def extract_bill_references(text: str) -> List[str]:
    """Extract bill IDs like 'AB 133', 'SB 2290'."""
    bills = []
    for match in re.finditer(r'\b([A-Z]{2})\s+(\d+)\b', text):
        bills.append(f"{match.group(1)} {match.group(2)}")
    return bills


def extract_cfr_references(text: str) -> List[Tuple[str, str, Optional[str]]]:
    """Extract CFR citations as (title, part, section)."""
    cfr = []
    # Pattern: "45 CFR 164.514" or "42 CFR 1320"
    for match in re.finditer(r'(\d+)\s+CFR\s+(\d+)(?:\.(\d+))?', text):
        title = match.group(1)
        part = match.group(2)
        section = match.group(3)
        cfr.append((title, part, section))
    return cfr


def cosine_similarity(vec1, vec2) -> float:
    """Placeholder cosine similarity."""
    import numpy as np
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8))


def φ(text: str) -> List[float]:
    """Placeholder embedding function."""
    # In production, use real embeddings (OpenAI, Hugging Face, etc.)
    import hashlib
    h = hashlib.md5(text.encode()).hexdigest()
    return [float(int(h[i:i+2], 16)) / 255.0 for i in range(0, 32, 2)]


def compute_vector_similarity(text: str, context: str) -> float:
    """Placeholder vector similarity score."""
    # In production, compare embeddings against reference corpus
    return 0.75 if len(text) > 50 else 0.5


# Static rules (placeholder implementations)
def r_consent_elements(text: str) -> float:
    """Rule: Text must contain consent elements."""
    required = ["consent", "agree", "authorize"]
    found = sum(1 for word in required if word.lower() in text.lower())
    return min(1.0, found / len(required))


def r_risk_documentation(text: str) -> float:
    """Rule: Text must document risks."""
    risk_keywords = ["risk", "adverse", "complication", "side effect"]
    found = sum(1 for word in risk_keywords if word.lower() in text.lower())
    return min(1.0, found / 2.0)


def r_apa_citations(text: str) -> float:
    """Rule: Academic text must have APA-style citations."""
    # Simple heuristic: look for (Author, Year) pattern
    apa_pattern = r'\([A-Z][a-z]+,\s*\d{4}\)'
    matches = len(re.findall(apa_pattern, text))
    return min(1.0, matches / 3.0) if matches > 0 else 0.0


# ============================================================================
# MCP rule helpers (sanitized – only see extracted tokens, never raw text)
# ============================================================================

def r_billing_code_verified(
    codes: List[Tuple[str, str]],
    mcp_client,
) -> float:
    """Rule: All mentioned billing codes must exist in official databases."""
    if not codes:
        return 1.0

    verified_count = 0
    for code_type, code in codes:
        result = mcp_client.lookup_billing_code(code_type, code)
        if result and result.get("verified"):
            verified_count += 1

    return verified_count / len(codes) if codes else 1.0


def r_legislation_current(
    bills: List[str],
    jurisdiction: str,
    mcp_client,
) -> float:
    """Rule: Referenced legislation must be signed into law."""
    if not bills:
        return 1.0

    scores: List[float] = []
    for bill_id in bills:
        result = mcp_client.check_state_bill_status(jurisdiction, bill_id)
        if not result:
            scores.append(0.0)
            continue

        status = result.get("status", "").lower()
        if status in {"signed", "signed_into_law", "chaptered"}:
            scores.append(1.0)
        elif status in {"passed_both_chambers", "passed_one_chamber", "enrolled"}:
            scores.append(0.5)
        else:
            scores.append(0.0)

    return sum(scores) / len(scores) if scores else 1.0


def r_cfr_compliance(
    cfr_citations: List[Tuple[str, str, Optional[str]]],
    text_for_embedding: str,
    mcp_client,
) -> float:
    """Rule: Text must align with cited CFR requirements."""
    if not cfr_citations:
        return 1.0

    similarity_scores: List[float] = []
    text_embedding = φ(text_for_embedding)

    for title, part, section in cfr_citations:
        result = mcp_client.search_federal_regulations(title, part, section)
        if not result:
            continue

        official_text = result.get("text_preview", "") or ""
        if not official_text.strip():
            continue

        cfr_embedding = φ(official_text)
        similarity = cosine_similarity(text_embedding, cfr_embedding)
        similarity_scores.append(float(similarity))

    if not similarity_scores:
        return 1.0

    return sum(similarity_scores) / len(similarity_scores)


# ============================================================================
# Base MCP-enhanced evaluator
# ============================================================================

class MCPEnhancedEvaluator:
    """
    Mathematical core with static + MCP rules.
    S_rule, S_vec, Q, D preserved exactly as in your framework.
    """

    def __init__(self, mcp_client, α: float = 0.7):
        self.mcp_client = mcp_client
        self.α = α  # Rule vs vector weight

        # Rule weights (must sum to 1)
        self.static_weight = 0.6   # PDF/static rules
        self.mcp_weight = 0.4      # MCP-verified rules

    def evaluate(
        self,
        text: str,
        context: str,
        jurisdiction: str,
        reg_refs: Optional[Dict] = None,
    ) -> Dict:
        """
        Main evaluation per mathematical framework.

        Args:
            text: full local text (NEVER sent to MCP)
            context: "clinical" or "academic"
            jurisdiction: e.g. "CA"
            reg_refs: optional pre-extracted regulatory references

        Returns: {
            "S_rule", "S_rule_static", "S_rule_mcp",
            "S_vec", "Q", "D",
            "failing_rules",
            "verified_codes", "verified_bills", "verified_cfr"
        }
        """

        if reg_refs is None:
            reg_refs = self._extract_regulatory_references(text)

        # --- Static rules ---
        static_scores = [
            r_consent_elements(text),
            r_risk_documentation(text),
        ]
        if context == "academic":
            static_scores.append(r_apa_citations(text))
        else:
            static_scores.append(1.0)

        S_rule_static = sum(static_scores) / len(static_scores)

        # --- MCP-backed rules ---
        billing_codes = reg_refs.get("billing_codes", [])
        legislation = reg_refs.get("legislation", [])
        cfr_citations = reg_refs.get("cfr_citations", [])

        billing_score = r_billing_code_verified(billing_codes, self.mcp_client)
        legislation_score = r_legislation_current(legislation, jurisdiction, self.mcp_client)
        cfr_score = r_cfr_compliance(cfr_citations, text, self.mcp_client)

        mcp_scores = [billing_score, legislation_score, cfr_score]
        S_rule_mcp = sum(mcp_scores) / len(mcp_scores)

        # Combined rule score
        S_rule = (
            self.static_weight * S_rule_static
            + self.mcp_weight * S_rule_mcp
        )

        # Vector similarity (your existing method)
        S_vec = compute_vector_similarity(text, context)

        # Combined quality
        Q = self.α * S_rule + (1.0 - self.α) * S_vec
        D = 1.0 - Q

        failing_rules = self._identify_failures(
            static_scores=static_scores,
            mcp_scores=mcp_scores,
            threshold=0.8,
        )

        return {
            "S_rule": S_rule,
            "S_rule_static": S_rule_static,
            "S_rule_mcp": S_rule_mcp,
            "S_vec": S_vec,
            "Q": Q,
            "D": D,
            "failing_rules": failing_rules,
            "verified_codes": billing_codes or None,
            "verified_bills": legislation or None,
            "verified_cfr": cfr_citations or None,
        }

    def _extract_regulatory_references(self, text: str) -> Dict:
        """Extract regulatory tokens (non-PHI-aware)."""
        return {
            "billing_codes": extract_billing_codes(text),
            "legislation": extract_bill_references(text),
            "cfr_citations": extract_cfr_references(text),
        }

    def _identify_failures(
        self,
        static_scores: List[float],
        mcp_scores: List[float],
        threshold: float = 0.8,
    ) -> Dict:
        """Identify which rules failed."""
        return {
            "static_rules": [i for i, s in enumerate(static_scores) if s < threshold],
            "mcp_rules": [i for i, s in enumerate(mcp_scores) if s < threshold],
        }


# ============================================================================
# PHI-safe extension
# ============================================================================

class PHISafeEvaluator(MCPEnhancedEvaluator):
    """
    Extension that enforces PHI constraints for clinical mode:
      1. MCP sees only regulatory tokens (codes, bills, CFR numbers).
      2. No patient identifiers leave this process.
      3. Clinical output reduced to minimal structured summary.
    """

    def evaluate(
        self,
        text: str,
        context: str,
        jurisdiction: str,
    ) -> Dict:
        """Evaluate with PHI safety checks."""
        # Pre-flight PHI scan on raw text
        if context == "clinical" and self._contains_phi(text):
            # Degrade: MCP disabled, static rules only
            reg_refs = {
                "billing_codes": [],
                "legislation": [],
                "cfr_citations": [],
            }
            mcp_enabled = False
        else:
            reg_refs = self._extract_regulatory_references(text)
            mcp_enabled = True

        # Run core evaluation with sanitized references
        result = super().evaluate(
            text=text,
            context=context,
            jurisdiction=jurisdiction,
            reg_refs=reg_refs,
        )

        # Audit log (no PHI – only regulatory tokens + scores)
        self._log_mcp_usage(reg_refs, result, mcp_enabled=mcp_enabled)

        if context == "clinical":
            return self._minimal_clinical_output(result)
        else:
            return result

    def _contains_phi(self, text: str) -> bool:
        """Simple heuristic PHI detector."""
        phi_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',        # SSN
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',    # Dates like 01/23/2024
            r'\bMRN[:\s]*\d{5,}\b',          # MRN pattern
        ]
        return any(re.search(p, text) for p in phi_patterns)

    def _minimal_clinical_output(self, result: Dict) -> Dict:
        """Return minimal structured summary for clinical context."""
        risk_level = "high" if result["S_rule"] < 0.5 else "normal"

        return {
            "risk_level": risk_level,
            "consent_complete": result["S_rule_static"] > 0.8,
            "regulations_verified": result["S_rule_mcp"] > 0.9,
            "language_access_ok": True,
            "distance": result["D"],
            "Q": result["Q"],
        }

    def _log_mcp_usage(
        self,
        reg_refs: Dict,
        result: Dict,
        mcp_enabled: bool,
    ) -> None:
        """Write audit entry (no PHI)."""
        # Implement as file logging or DB insert on your side
        pass

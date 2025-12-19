from typing import Optional, Dict, Any

def r_billing_code_verified(mcp_result: Optional[Dict[str, Any]]) -> float:
    """
    Return 1.0 if billing code is valid and active, 0.0 if invalid, 0.5 if unknown.

    Args:
        mcp_result: Result dictionary from MCP billing tool.

    Returns:
        Score (0.0 to 1.0)
    """
    if not mcp_result:
        return 0.5
    status = mcp_result.get("status")  # e.g. "active", "deleted", "unknown"
    if status == "active":
        return 1.0
    if status in {"deleted", "invalid"}:
        return 0.0
    return 0.5


def r_legislation_current(bill_result: Optional[Dict[str, Any]]) -> float:
    """
    Weight based on bill status (e.g., 'enacted' > 'introduced').

    Args:
        bill_result: Result dictionary from MCP bill tool.

    Returns:
        Score (0.0 to 1.0)
    """
    if not bill_result:
        return 0.5
    status = bill_result.get("status")  # "passed", "failed", "introduced", etc.
    if status in {"passed", "enacted"}:
        return 1.0
    if status in {"failed", "vetoed"}:
        return 0.0
    return 0.7  # in process


def r_cfr_compliance(cfr_result: Optional[Dict[str, Any]]) -> float:
    """
    Compare text against CFR/USC hits; 1.0 if fully aligned, lower if conflicts found.

    Args:
        cfr_result: Result dictionary from MCP CFR tool.

    Returns:
        Score (0.0 to 1.0)
    """
    if not cfr_result:
        return 0.5
    conflicts = cfr_result.get("conflicts", 0)
    if conflicts == 0:
        return 1.0
    if conflicts <= 2:
        return 0.6
    return 0.2


def compute_quality(
    t: str,
    c: Optional[Dict[str, Any]],
    static_rules_score: float,
    vector_score: float,
    billing_rule_score: float,
    legislation_rule_score: float,
    cfr_rule_score: float,
) -> float:
    """
    Quality score Q(t, c) aligned with legacy IP calibration (α=0.7).

    Combines rules and vector similarity using the hierarchical framework:
    Q = α * S_rule + (1-α) * S_vec
    S_rule = 0.6 * S_rule_static + 0.4 * S_rule_mcp
    """
    # Legacy Calibration Constants
    ALPHA = 0.7
    W_STATIC = 0.6
    W_MCP = 0.4

    # Calculate hierarchical components
    s_rule_mcp = (billing_rule_score + legislation_rule_score + cfr_rule_score) / 3.0
    s_rule = (W_STATIC * static_rules_score) + (W_MCP * s_rule_mcp)

    # Final Quality Score
    q = (ALPHA * s_rule) + ((1.0 - ALPHA) * vector_score)
    return q

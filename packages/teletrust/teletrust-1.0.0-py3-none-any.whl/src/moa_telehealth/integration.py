# moa_v1 Integration Shim
# Cleanly consumes moa_telehealth package with single import point
# This reduces refactor blast-radius when moa_telehealth internals change.

from __future__ import annotations
from typing import Any, Dict, Optional

# Import from the stable PyPI API surface
try:
    from moa_telehealth import (
        govern,
        TelehealthGovernor,
        GovernanceResult,
        ComplianceEngine,
        ESMCompressor,
        MoaUsageLedger,
        __version__ as moa_version,
    )

    MOA_AVAILABLE = True
except ImportError:
    # Fallback: try relative import if running from source
    try:
        import sys

        sys.path.insert(0, r"M:\source\repos\moa_telehealth_governor\src")
        from moa_telehealth import govern, TelehealthGovernor, GovernanceResult

        MOA_AVAILABLE = True
    except ImportError:
        MOA_AVAILABLE = False
        moa_version = "0.0.0"


def check_moa_integration() -> Dict[str, Any]:
    """Check if moa_telehealth is properly integrated."""
    return {
        "available": MOA_AVAILABLE,
        "version": moa_version if MOA_AVAILABLE else None,
        "status": "OK" if MOA_AVAILABLE else "NOT_INSTALLED",
    }


def process_with_governance(
    session_id: str, user_input: str, context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process user input through MOA governance.

    This is the single integration point for moa_v1 to call moa_telehealth.
    All governance logic flows through here.

    Returns:
        Dict with: zone, risk_score, output_text, action_log, compliance_verdict
    """
    if not MOA_AVAILABLE:
        return {
            "error": "moa_telehealth not installed",
            "zone": "RED",
            "risk_score": 1.0,
            "output_text": "Governance engine unavailable. Install with: pip install moa-telehealth",
            "action_log": ["MOA_UNAVAILABLE"],
        }

    result = govern(session_id, user_input, context)

    return {
        "zone": result.zone,
        "risk_score": result.risk_score,
        "output_text": result.output_text,
        "action_log": result.action_log,
        "compliance_verdict": result.compliance_verdict,
        "billing": result.billing,
        "evidence": result.evidence,
        "prime_code_macro": result.prime_code_macro,
    }


# Export clean interface
__all__ = [
    "check_moa_integration",
    "process_with_governance",
    "TelehealthGovernor",
    "GovernanceResult",
    "MOA_AVAILABLE",
]


if __name__ == "__main__":
    # Quick test
    status = check_moa_integration()
    print(f"MOA Integration: {status}")

    if status["available"]:
        result = process_with_governance(
            "test_session", "Patient reports feeling better today."
        )
        print(f"Zone: {result['zone']}")
        print(f"Risk: {result['risk_score']}")

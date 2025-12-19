# moa_telehealth - Stable Public API
# This module re-exports the stable public surface for PyPI consumption.
# Internal implementation is in src/governor/ - this wrapper provides clean imports.

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Dict

# Version - keep in sync with pyproject.toml
__version__ = "2.0.0"
__author__ = "Michael Ordon"
__email__ = "grzywajk@gmail.com"

# Re-export main classes
try:
    from src.governor.telehealth_governor import GovernanceResult, TelehealthGovernor
except ImportError:
    # Fallback for when installed as package vs running from source
    from .governor.telehealth_governor import GovernanceResult, TelehealthGovernor

# Re-export compliance engine
try:
    from src.compliance.engine import ComplianceEngine, ComplianceResult
except ImportError:
    from .compliance.engine import ComplianceEngine, ComplianceResult

# Re-export physics modules (spectral analysis)
try:
    from src.physics.esm_compressor import ESMCompressor
except ImportError:
    from .physics.esm_compressor import ESMCompressor

# Re-export billing
try:
    from src.billing.moa_usage_ledger import MoaUsageLedger
except ImportError:
    from .billing.moa_usage_ledger import MoaUsageLedger


def govern(
    session_id: str,
    user_input: str,
    context: Dict[str, Any] | None = None,
    config: Dict[str, Any] | None = None
) -> GovernanceResult:
    """
    One-shot governance call. Creates a governor, processes input, returns result.

    This is the recommended entry point for simple integrations.

    Args:
        session_id: Unique session identifier
        user_input: User message to process
        context: Optional context dict with patient_state, provider_state, etc.
        config: Optional governor configuration

    Returns:
        GovernanceResult with zone, risk_score, output_text, etc.

    Example:
        >>> from moa_telehealth import govern
        >>> result = govern("sess_001", "Patient reports improved mood")
        >>> print(result.zone, result.risk_score)
        GREEN 0.15
    """
    gov = TelehealthGovernor(config)
    return gov.process_interaction(session_id, user_input, context)


# Public API surface
__all__ = [
    # Version
    "__version__",

    # Main function
    "govern",

    # Core classes
    "TelehealthGovernor",
    "GovernanceResult",
    "ComplianceEngine",
    "ComplianceResult",

    # Physics/Analysis
    "ESMCompressor",

    # Billing
    "MoaUsageLedger",
]

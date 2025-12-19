"""
Refusal Policy
==============
Determines when the system should say "I don't know" rather than confabulate.
Key to commercial credibility.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RefusalReason(Enum):
    """Why a response was refused."""
    LOW_CONFIDENCE = "confidence_below_threshold"
    NO_SOURCES = "no_source_citations"
    CONFLICTING_SOURCES = "sources_conflict"
    OUT_OF_SCOPE = "question_outside_domain"
    PHI_DETECTED = "phi_in_query"
    INJECTION_DETECTED = "prompt_injection_attempt"


@dataclass
class RefusalDecision:
    """The decision from RefusalPolicy."""
    should_refuse: bool
    reason: Optional[RefusalReason] = None
    message: str = ""
    confidence: float = 0.0
    source_count: int = 0


class RefusalPolicy:
    """
    Policy engine for deciding when to refuse vs respond.

    Thresholds calibrated for telehealth compliance:
    - High confidence required (0.7+)
    - Sources required for regulatory claims
    - Conservative on edge cases
    """

    def __init__(
        self,
        min_confidence: float = 0.7,
        require_sources: bool = True,
        min_sources: int = 1
    ):
        self.min_confidence = min_confidence
        self.require_sources = require_sources
        self.min_sources = min_sources

    def evaluate(
        self,
        confidence: float,
        source_count: int,
        has_conflicts: bool = False,
        is_in_scope: bool = True,
        phi_detected: bool = False,
        injection_detected: bool = False
    ) -> RefusalDecision:
        """
        Evaluate whether to refuse a response.

        Args:
            confidence: Model's confidence score (0-1)
            source_count: Number of sources supporting the response
            has_conflicts: Whether sources conflict with each other
            is_in_scope: Whether question is in telehealth domain
            phi_detected: Whether PHI was detected in query
            injection_detected: Whether prompt injection was detected

        Returns:
            RefusalDecision
        """
        # Priority 1: Security blocks (always refuse)
        if phi_detected:
            return RefusalDecision(
                should_refuse=True,
                reason=RefusalReason.PHI_DETECTED,
                message="This service does not process protected health information. Please remove patient identifiers.",
                confidence=confidence,
                source_count=source_count
            )

        if injection_detected:
            return RefusalDecision(
                should_refuse=True,
                reason=RefusalReason.INJECTION_DETECTED,
                message="Request could not be processed. Please rephrase your question.",
                confidence=confidence,
                source_count=source_count
            )

        # Priority 2: Scope check
        if not is_in_scope:
            return RefusalDecision(
                should_refuse=True,
                reason=RefusalReason.OUT_OF_SCOPE,
                message="This question is outside the telehealth compliance domain. I can only answer questions about telehealth regulations.",
                confidence=confidence,
                source_count=source_count
            )

        # Priority 3: Source requirements
        if self.require_sources and source_count < self.min_sources:
            return RefusalDecision(
                should_refuse=True,
                reason=RefusalReason.NO_SOURCES,
                message="I cannot find authoritative sources to answer this question. Please consult official regulatory documentation.",
                confidence=confidence,
                source_count=source_count
            )

        if has_conflicts:
            return RefusalDecision(
                should_refuse=True,
                reason=RefusalReason.CONFLICTING_SOURCES,
                message="Sources conflict on this topic. I recommend consulting a compliance attorney for authoritative guidance.",
                confidence=confidence,
                source_count=source_count
            )

        # Priority 4: Confidence threshold
        if confidence < self.min_confidence:
            return RefusalDecision(
                should_refuse=True,
                reason=RefusalReason.LOW_CONFIDENCE,
                message=f"I'm not confident enough in this answer (confidence: {confidence:.0%}). Please verify with authoritative sources.",
                confidence=confidence,
                source_count=source_count
            )

        # All checks passed - allow response
        return RefusalDecision(
            should_refuse=False,
            confidence=confidence,
            source_count=source_count
        )


# Default policy instance for telehealth
TELEHEALTH_POLICY = RefusalPolicy(
    min_confidence=0.7,
    require_sources=True,
    min_sources=1
)


# Stricter policy for court-ready mode
COURT_READY_POLICY = RefusalPolicy(
    min_confidence=0.9,
    require_sources=True,
    min_sources=2
)

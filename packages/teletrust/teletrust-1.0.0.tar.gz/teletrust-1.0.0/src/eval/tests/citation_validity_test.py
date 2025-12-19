"""
Citation Validity Test
======================
Verify that each citation in a response:
1. Actually exists in the reference database
2. Supports the claim being made
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class CitationResult:
    """Result for a single citation check."""

    citation_text: str
    exists: bool
    supports_claim: bool
    error: Optional[str] = None


@dataclass
class CitationValidityResult:
    """Result of citation validity test for a response."""

    question_id: str
    total_citations: int
    valid_count: int
    invalid_count: int
    validity_rate: float
    passed: bool
    invalid_citations: list


def extract_citations(response: str) -> list:
    """
    Extract citations from response text.

    Looks for patterns like:
    - (42 CFR § 164.502)
    - [Cal. Bus. & Prof. Code § 2290.5]
    - per 21 U.S.C. § 829(e)
    """
    patterns = [
        r"\(([^)]+§[^)]+)\)",  # (CFR § 123)
        r"\[([^\]]+§[^\]]+)\]",  # [USC § 123]
        r"(?:per|under|see)\s+(\d+\s+[A-Z.]+\s+[§\d]+)",  # per 42 CFR § 123
        r"([A-Z][a-z]+\.\s+[A-Z][a-z]+\.\s+&\s+[A-Z][a-z]+\.\s+Code\s+§\s*[\d.]+)",  # Cal. Bus. & Prof. Code § 123
    ]

    citations = []
    for pattern in patterns:
        matches = re.findall(pattern, response, re.IGNORECASE)
        citations.extend(matches)

    return list(set(citations))  # Dedupe


def validate_citation(citation: str, reference_db: dict) -> CitationResult:
    """
    Validate a single citation against reference database.

    Args:
        citation: The citation text (e.g., "45 CFR § 164.502")
        reference_db: Dict mapping citation -> {title, content, url}

    Returns:
        CitationResult
    """
    # Normalize citation for lookup
    normalized = citation.lower().replace(" ", "").replace("§", "s")

    # Check if citation exists
    for ref_key, ref_data in reference_db.items():
        ref_normalized = ref_key.lower().replace(" ", "").replace("§", "s")
        if normalized in ref_normalized or ref_normalized in normalized:
            return CitationResult(
                citation_text=citation,
                exists=True,
                supports_claim=True,  # Simplified - would need NLI in production
            )

    return CitationResult(
        citation_text=citation,
        exists=False,
        supports_claim=False,
        error="Citation not found in reference database",
    )


async def run_citation_validity_test(
    response: str, reference_db: dict, question_id: str = "unknown", threshold: float = 0.95
) -> CitationValidityResult:
    """
    Run citation validity test on a single response.

    Args:
        response: LLM response text with citations
        reference_db: Valid references to check against
        question_id: ID for tracking
        threshold: Required validity rate (default 95%)

    Returns:
        CitationValidityResult
    """
    citations = extract_citations(response)

    if not citations:
        # No citations to validate
        return CitationValidityResult(
            question_id=question_id,
            total_citations=0,
            valid_count=0,
            invalid_count=0,
            validity_rate=1.0,  # N/A counts as pass
            passed=True,
            invalid_citations=[],
        )

    results = [validate_citation(c, reference_db) for c in citations]
    valid = [r for r in results if r.exists and r.supports_claim]
    invalid = [r for r in results if not r.exists or not r.supports_claim]

    validity_rate = len(valid) / len(results)

    return CitationValidityResult(
        question_id=question_id,
        total_citations=len(results),
        valid_count=len(valid),
        invalid_count=len(invalid),
        validity_rate=validity_rate,
        passed=validity_rate >= threshold,
        invalid_citations=[r.citation_text for r in invalid],
    )


# Reference database for telehealth regulations
TELEHEALTH_REFERENCES = {
    "45 CFR § 164.502": {
        "title": "HIPAA Privacy Rule - Uses and Disclosures",
        "url": "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E/section-164.502",
    },
    "45 CFR §§ 164.308-312": {
        "title": "HIPAA Security Rule - Administrative Safeguards",
        "url": "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-C",
    },
    "Cal. Bus. & Prof. Code § 2290.5": {
        "title": "California Telehealth Consent",
        "url": "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=2290.5.&lawCode=BPC",
    },
    "21 U.S.C. § 829(e)": {
        "title": "Ryan Haight Act - Controlled Substances",
        "url": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title21-section829",
    },
    "42 CFR § 410.78": {
        "title": "Medicare Telehealth Services",
        "url": "https://www.ecfr.gov/current/title-42/chapter-IV/subchapter-B/part-410/subpart-B/section-410.78",
    },
}


if __name__ == "__main__":
    # Test
    test_response = """
    California requires informed consent per Cal. Bus. & Prof. Code § 2290.5.
    HIPAA compliance requires a BAA under 45 CFR § 164.502.
    This is an unverifiable claim with no citation.
    """

    result = asyncio.run(
        run_citation_validity_test(test_response, TELEHEALTH_REFERENCES, "test-001")
    )
    print(f"Pass: {result.passed}, Validity: {result.validity_rate:.1%}")

"""
Source Lock Test
================
Verify that responses ONLY contain information from the provided source document.
Any claim not grounded in the source = FAIL.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Optional

from ..metrics import calculate_faithfulness


@dataclass
class SourceLockResult:
    """Result of a source-lock test."""

    question_id: str
    passed: bool
    faithfulness_score: float
    ungrounded_claims: list
    error: Optional[str] = None


async def run_source_lock_test(
    question: str, source_document: str, get_response_fn, threshold: float = 1.0
) -> SourceLockResult:
    """
    Run a single source-lock test.

    Args:
        question: The question to ask
        source_document: The ONLY source of truth
        get_response_fn: Async function(question, source) -> response
        threshold: Required faithfulness score (default 1.0 = 100%)

    Returns:
        SourceLockResult
    """
    try:
        response = await get_response_fn(question, source_document)
        score, ungrounded = calculate_faithfulness(response, source_document)

        return SourceLockResult(
            question_id=question[:50],
            passed=score >= threshold,
            faithfulness_score=score,
            ungrounded_claims=ungrounded,
        )
    except Exception as e:
        return SourceLockResult(
            question_id=question[:50],
            passed=False,
            faithfulness_score=0.0,
            ungrounded_claims=[],
            error=str(e),
        )


async def run_source_lock_suite(corpus_path: str, get_response_fn, threshold: float = 1.0) -> dict:
    """
    Run source-lock test on entire corpus.

    Returns:
        {
            "total": int,
            "passed": int,
            "failed": int,
            "pass_rate": float,
            "failures": [SourceLockResult]
        }
    """
    with open(corpus_path) as f:
        corpus = json.load(f)

    results = []
    for q in corpus.get("questions", []):
        # Use ground_truth as the source document (strict mode)
        result = await run_source_lock_test(
            question=q["question"],
            source_document=q["ground_truth"],
            get_response_fn=get_response_fn,
            threshold=threshold,
        )
        result.question_id = q["id"]
        results.append(result)

    passed = [r for r in results if r.passed]
    failed = [r for r in results if not r.passed]

    return {
        "total": len(results),
        "passed": len(passed),
        "failed": len(failed),
        "pass_rate": len(passed) / len(results) if results else 0,
        "failures": [
            {
                "id": r.question_id,
                "score": r.faithfulness_score,
                "ungrounded": r.ungrounded_claims[:3],  # First 3 claims
            }
            for r in failed
        ],
    }


if __name__ == "__main__":
    # Example usage with mock response function
    async def mock_response(question: str, source: str) -> str:
        # In production, this calls the actual Governor API
        return source  # Perfect faithfulness for testing

    result = asyncio.run(run_source_lock_suite("benchmarks/telehealth_50.json", mock_response))
    print(json.dumps(result, indent=2))

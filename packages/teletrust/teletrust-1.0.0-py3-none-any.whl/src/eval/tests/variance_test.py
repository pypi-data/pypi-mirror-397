"""
Variance Test
=============
Run same prompt multiple times with different seeds/temperatures.
If "facts" change between runs, it indicates confabulation risk.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Awaitable, Callable

from ..metrics import calculate_variance


@dataclass
class VarianceResult:
    """Result of variance test."""

    question_id: str
    num_runs: int
    variance_score: float
    is_stable: bool
    passed: bool
    sample_differences: list


async def run_variance_test(
    question: str,
    get_response_fn: Callable[[str, float], Awaitable[str]],
    num_runs: int = 5,
    temperatures: list = None,
    threshold: float = 0.05,
    question_id: str = "unknown",
) -> VarianceResult:
    """
    Run variance test on a single question.

    Args:
        question: The question to ask repeatedly
        get_response_fn: Async function(question, temperature) -> response
        num_runs: Number of times to run (default 5)
        temperatures: List of temperatures to use, or None for default [0.1, 0.3, 0.5, 0.7, 0.9]
        threshold: Max acceptable variance (default 5%)
        question_id: ID for tracking

    Returns:
        VarianceResult
    """
    if temperatures is None:
        temperatures = [0.1, 0.3, 0.5, 0.7, 0.9][:num_runs]

    responses = []
    for temp in temperatures[:num_runs]:
        try:
            response = await get_response_fn(question, temp)
            responses.append(response)
        except Exception as e:
            responses.append(f"ERROR: {e}")

    variance, is_stable = calculate_variance(responses)

    # Find example differences
    differences = []
    if len(responses) >= 2:
        # Compare first two responses for concrete examples
        words_0 = set(responses[0].lower().split())
        words_1 = set(responses[1].lower().split())
        only_in_0 = words_0 - words_1
        only_in_1 = words_1 - words_0

        if only_in_0 or only_in_1:
            differences = [
                f"Run 1 unique: {list(only_in_0)[:5]}",
                f"Run 2 unique: {list(only_in_1)[:5]}",
            ]

    return VarianceResult(
        question_id=question_id,
        num_runs=len(responses),
        variance_score=variance,
        is_stable=is_stable,
        passed=variance <= threshold,
        sample_differences=differences,
    )


async def run_variance_suite(
    corpus_path: str,
    get_response_fn: Callable[[str, float], Awaitable[str]],
    num_runs: int = 3,
    threshold: float = 0.05,
) -> dict:
    """
    Run variance test on entire corpus.

    Returns:
        {
            "total": int,
            "stable": int,
            "unstable": int,
            "avg_variance": float,
            "unstable_questions": [VarianceResult]
        }
    """
    with open(corpus_path) as f:
        corpus = json.load(f)

    results = []
    for q in corpus.get("questions", []):
        result = await run_variance_test(
            question=q["question"],
            get_response_fn=get_response_fn,
            num_runs=num_runs,
            threshold=threshold,
            question_id=q["id"],
        )
        results.append(result)

    stable = [r for r in results if r.is_stable]
    unstable = [r for r in results if not r.is_stable]
    avg_variance = sum(r.variance_score for r in results) / len(results) if results else 0

    return {
        "total": len(results),
        "stable": len(stable),
        "unstable": len(unstable),
        "avg_variance": f"{avg_variance:.2%}",
        "pass": len(unstable) == 0,
        "unstable_questions": [
            {
                "id": r.question_id,
                "variance": f"{r.variance_score:.2%}",
                "differences": r.sample_differences,
            }
            for r in unstable[:5]  # Top 5 worst
        ],
    }


if __name__ == "__main__":
    # Mock test
    call_count = 0

    async def mock_llm(question: str, temp: float) -> str:
        global call_count
        call_count += 1
        # Simulate slight variance
        base = "California requires informed consent for telehealth."
        if temp > 0.5:
            base += f" This includes documentation requirements. (Run {call_count})"
        return base

    result = asyncio.run(
        run_variance_test(
            "What are California telehealth consent requirements?",
            mock_llm,
            num_runs=3,
            question_id="test-variance",
        )
    )
    print(f"Stable: {result.is_stable}, Variance: {result.variance_score:.2%}")

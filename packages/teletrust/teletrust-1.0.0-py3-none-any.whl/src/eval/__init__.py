"""
Eval Harness - Hallucination Detection Framework
================================================
Provides measurable benchmarks for LLM response quality.
"""

from .harness import EvalHarness, run_benchmark
from .metrics import calculate_citation_validity, calculate_faithfulness, calculate_variance

__all__ = [
    "EvalHarness",
    "run_benchmark",
    "calculate_faithfulness",
    "calculate_citation_validity",
    "calculate_variance",
]

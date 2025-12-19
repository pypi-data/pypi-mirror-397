"""
Eval Harness - Core Runner
==========================
Runs benchmark corpus through the Governor API and scores responses.
"""

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class EvalResult:
    """Result of a single benchmark question evaluation."""

    question_id: str
    question: str
    expected_answer: str
    actual_answer: str
    source_citation: str

    # Scores
    grounded: bool = False
    citation_valid: bool = False
    refused: bool = False

    # Metadata
    confidence: float = 0.0
    latency_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class BenchmarkReport:
    """Aggregate benchmark results."""

    corpus_name: str
    run_timestamp: str
    total_questions: int

    # Counts
    grounded_count: int = 0
    ungrounded_count: int = 0
    citation_valid_count: int = 0
    citation_invalid_count: int = 0
    refusal_count: int = 0
    error_count: int = 0

    # Rates
    grounded_rate: float = 0.0
    citation_validity_rate: float = 0.0
    refusal_rate: float = 0.0

    results: list = field(default_factory=list)

    def calculate_rates(self):
        """Calculate aggregate rates from counts."""
        if self.total_questions > 0:
            self.grounded_rate = self.grounded_count / self.total_questions
            self.citation_validity_rate = self.citation_valid_count / self.total_questions
            self.refusal_rate = self.refusal_count / self.total_questions

    def to_dict(self) -> dict:
        return {
            "corpus_name": self.corpus_name,
            "run_timestamp": self.run_timestamp,
            "metrics": {
                "grounded_rate": f"{self.grounded_rate:.1%}",
                "citation_validity_rate": f"{self.citation_validity_rate:.1%}",
                "refusal_rate": f"{self.refusal_rate:.1%}",
                "ungrounded_count": self.ungrounded_count,
                "error_count": self.error_count,
            },
            "pass": self.grounded_rate >= 0.98 and self.citation_validity_rate >= 0.95,
        }


class EvalHarness:
    """
    Evaluation harness for hallucination detection.

    Usage:
        harness = EvalHarness(corpus_path="benchmarks/telehealth_50.json")
        report = await harness.run()
        print(report.to_dict())
    """

    def __init__(self, corpus_path: str, api_url: str = "http://localhost:8000"):
        self.corpus_path = Path(corpus_path)
        self.api_url = api_url
        self.corpus = self._load_corpus()

    def _load_corpus(self) -> dict:
        """Load benchmark corpus from JSON file."""
        with open(self.corpus_path) as f:
            return json.load(f)

    async def run(self, subset: Optional[list] = None) -> BenchmarkReport:
        """
        Run full benchmark evaluation.

        Args:
            subset: Optional list of question IDs to run (for debugging)

        Returns:
            BenchmarkReport with aggregate scores
        """
        questions = self.corpus.get("questions", [])
        if subset:
            questions = [q for q in questions if q["id"] in subset]

        report = BenchmarkReport(
            corpus_name=self.corpus["metadata"]["name"],
            run_timestamp=datetime.now().isoformat(),
            total_questions=len(questions),
        )

        for question in questions:
            result = await self._evaluate_question(question)
            report.results.append(result)

            # Update counts
            if result.error:
                report.error_count += 1
            elif result.refused:
                report.refusal_count += 1
            else:
                if result.grounded:
                    report.grounded_count += 1
                else:
                    report.ungrounded_count += 1

                if result.citation_valid:
                    report.citation_valid_count += 1
                else:
                    report.citation_invalid_count += 1

        report.calculate_rates()
        return report

    async def _evaluate_question(self, question: dict) -> EvalResult:
        """Evaluate a single question against the Governor API."""
        import httpx

        result = EvalResult(
            question_id=question["id"],
            question=question["question"],
            expected_answer=question["ground_truth"],
            actual_answer="",
            source_citation=question["source_citation"],
        )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                start = asyncio.get_event_loop().time()

                # Call the Governor API
                response = await client.post(
                    f"{self.api_url}/govern",
                    json={
                        "prompt": question["question"],
                        "context": question.get("source_document", ""),
                        "require_sources": True,
                    },
                )

                result.latency_ms = (asyncio.get_event_loop().time() - start) * 1000

                if response.status_code == 200:
                    data = response.json()
                    result.actual_answer = data.get("response", "")
                    result.confidence = data.get("confidence", 0.0)
                    result.grounded = data.get("grounded", False)
                    result.citation_valid = self._validate_citation(
                        data.get("sources", []), question["source_citation"]
                    )
                elif response.status_code == 422:
                    # Refusal (uncertainty too high)
                    result.refused = True
                else:
                    result.error = f"HTTP {response.status_code}"

        except Exception as e:
            result.error = str(e)

        return result

    def _validate_citation(self, actual_sources: list, expected_citation: str) -> bool:
        """Check if the expected citation appears in actual sources."""
        expected_parts = expected_citation.lower().split(";")
        for part in expected_parts:
            part = part.strip()
            if any(part in str(src).lower() for src in actual_sources):
                return True
        return False


async def run_benchmark(corpus_path: str, output_path: Optional[str] = None) -> BenchmarkReport:
    """
    Convenience function to run a benchmark and optionally save results.

    Args:
        corpus_path: Path to benchmark JSON
        output_path: Optional path to save results JSON

    Returns:
        BenchmarkReport
    """
    harness = EvalHarness(corpus_path)
    report = await harness.run()

    if output_path:
        with open(output_path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

    return report


if __name__ == "__main__":
    # CLI entry point
    import sys

    corpus = sys.argv[1] if len(sys.argv) > 1 else "benchmarks/telehealth_50.json"
    output = sys.argv[2] if len(sys.argv) > 2 else None

    report = asyncio.run(run_benchmark(corpus, output))
    print(json.dumps(report.to_dict(), indent=2))

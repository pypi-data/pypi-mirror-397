#!/usr/bin/env python
"""
ESM Token Optimizer

Reduces LLM token usage by:
1. Detecting redundant/repetitive content via SSG fingerprints
2. Deduplicating similar text blocks
3. Compressing prompts while preserving semantic structure
4. Tracking token savings for cost optimization

Target: 30-66% token reduction on verbose prompts
"""

import numpy as np
import hashlib
import re
from typing import List, Tuple, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Import SSG components
try:
    from src.ssg.core import SSGCodec
    from src.ssg.geometry import ssg_geodesic_distance
except ImportError:
    SSGCodec = None
    ssg_geodesic_distance = None

# =============================================================================
# TOKEN ESTIMATION
# =============================================================================


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough: ~4 chars per token for English)."""
    return max(1, len(text) // 4)


def text_to_signal(text: str, window_size: int = 30) -> np.ndarray:
    """Convert text to numerical signal for SSG analysis."""
    # Use character codes as signal values
    codes = [ord(c) for c in text]

    # Pad or truncate to window_size
    if len(codes) < window_size:
        codes = codes + [0] * (window_size - len(codes))

    return np.array(codes[:window_size], dtype=float)


# =============================================================================
# DATACLASSES
# =============================================================================


@dataclass
class TokenMetrics:
    """Token usage metrics."""

    original_tokens: int = 0
    compressed_tokens: int = 0
    savings_tokens: int = 0
    savings_percent: float = 0.0
    blocks_removed: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def update(self, original: int, compressed: int, blocks: int = 0):
        self.original_tokens += original
        self.compressed_tokens += compressed
        self.savings_tokens = self.original_tokens - self.compressed_tokens
        self.savings_percent = (
            (self.savings_tokens / self.original_tokens * 100)
            if self.original_tokens > 0
            else 0
        )
        self.blocks_removed += blocks


@dataclass
class CompressionResult:
    """Result of text compression."""

    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    savings_percent: float
    removed_blocks: List[str] = field(default_factory=list)
    fingerprint_cache_hits: int = 0


# =============================================================================
# ESM TOKEN OPTIMIZER
# =============================================================================


class ESMTokenOptimizer:
    """
    Token optimizer using SSG spectral fingerprinting.

    Detects and removes:
    - Repetitive paragraphs
    - Redundant preambles
    - Duplicate context blocks
    - Verbose boilerplate
    """

    def __init__(
        self,
        window_size: int = 30,
        similarity_threshold: float = 0.85,
        min_block_size: int = 50,
        cache_size: int = 1000,
    ):
        self.window_size = window_size
        self.similarity_threshold = similarity_threshold
        self.min_block_size = min_block_size

        # Initialize SSG codec if available
        if SSGCodec:
            self.codec = SSGCodec(window_size=window_size)
        else:
            self.codec = None

        # Fingerprint cache for deduplication
        self.fingerprint_cache: Dict[str, np.ndarray] = {}
        self.cache_size = cache_size

        # Cumulative metrics
        self.metrics = TokenMetrics()

        # Boilerplate patterns to compress
        self.boilerplate_patterns = [
            (
                r"(?i)^(please note that|it's important to note that|as mentioned earlier|as previously stated)",
                "Note:",
            ),
            (r"(?i)^(in order to|for the purpose of)", "To"),
            (r"(?i)(at this point in time|at the current moment)", "now"),
            (r"(?i)(due to the fact that|because of the fact that)", "because"),
            (r"(?i)(in the event that|in case of)", "if"),
            (r"(?i)(a large number of|a significant number of)", "many"),
            (r"(?i)(in spite of the fact that)", "although"),
            (r"(?i)(has the ability to|is able to)", "can"),
            (r"(?i)(prior to|previous to)", "before"),
            (r"(?i)(subsequent to|following)", "after"),
        ]

    def _get_fingerprint(self, text: str) -> Any:
        """Get fingerprint for text block (SSG or Hash fallback)."""
        # 1. Try SSG Codec (Spectral Fingerprint)
        if self.codec:
            # Check cache
            text_hash = hashlib.md5(text.encode()).hexdigest()[:16]
            if text_hash in self.fingerprint_cache:
                return self.fingerprint_cache[text_hash]

            # Convert text to signal
            signal = text_to_signal(text, self.window_size)
            try:
                fingerprint = self.codec.encode(signal)
                # Cache management
                if len(self.fingerprint_cache) >= self.cache_size:
                    keys = list(self.fingerprint_cache.keys())[:100]
                    for k in keys:
                        del self.fingerprint_cache[k]
                self.fingerprint_cache[text_hash] = fingerprint
                return fingerprint
            except Exception:
                pass  # Fallback

        # 2. Fallback: Simple MD5 Hash (Exact Match dedupe)
        # If we don't have physics engine, we deduce exact duplicates
        return hashlib.md5(text.strip().encode()).hexdigest()

    def _calculate_similarity(self, fp1: Any, fp2: Any) -> float:
        """Calculate similarity between two fingerprints."""
        # Handle string hashes (Fallback mode)
        if isinstance(fp1, str) and isinstance(fp2, str):
            return 1.0 if fp1 == fp2 else 0.0

        # Handle SSG Vectors
        if hasattr(fp1, "shape") and hasattr(fp2, "shape"):  # numpy array check
            if ssg_geodesic_distance:
                dist = ssg_geodesic_distance(fp1, fp2)
                return 1.0 - (dist / np.pi)
            else:
                # Fallback to cosine similarity
                dot = np.dot(fp1, fp2)
                norm = np.linalg.norm(fp1) * np.linalg.norm(fp2)
                return dot / norm if norm > 0 else 0.0

        return 0.0

    def _split_into_blocks(self, text: str, aggressive: bool = False) -> List[str]:
        """Split text into semantic blocks."""
        # If aggressive, split on single newlines for chat/log deduplication
        if aggressive:
            # Split on single newlines
            blocks = text.split("\n")
        else:
            # Split on double newlines (paragraphs)
            blocks = re.split(r"\n\s*\n", text)

        # Also split on markdown headers if not aggressive
        if not aggressive:
            result = []
            for block in blocks:
                if block.strip():
                    sub_blocks = re.split(r"(?=^#{1,6}\s)", block, flags=re.MULTILINE)
                    result.extend([b.strip() for b in sub_blocks if b.strip()])
            return result

        return [b.strip() for b in blocks if b.strip()]

    def _compress_boilerplate(self, text: str) -> str:
        """Apply boilerplate compression patterns."""
        for pattern, replacement in self.boilerplate_patterns:
            text = re.sub(pattern, replacement, text)
        return text

    def _deduplicate_blocks(self, blocks: List[str]) -> Tuple[List[str], List[str]]:
        """Remove duplicate or highly similar blocks."""
        unique_blocks = []
        removed_blocks = []
        fingerprints = []

        for block in blocks:
            # For aggressive chat logs, min block size might need to be smaller?
            # Or reliance on fingerprint is enough.
            if len(block) < self.min_block_size:
                # If short, maybe keep it unless it's EXACT duplicate?
                # For now, keep logic simple: short blocks kept.
                unique_blocks.append(block)
                continue

            fp = self._get_fingerprint(block)

            if fp is None:
                unique_blocks.append(block)
                continue

            # Check similarity against existing fingerprints
            is_duplicate = False
            for existing_fp in fingerprints:
                similarity = self._calculate_similarity(fp, existing_fp)
                if similarity >= self.similarity_threshold:
                    is_duplicate = True
                    break

            if is_duplicate:
                removed_blocks.append(
                    block[:100] + "..." if len(block) > 100 else block
                )
            else:
                unique_blocks.append(block)
                fingerprints.append(fp)

        return unique_blocks, removed_blocks

    def compress(self, text: str, aggressive: bool = False) -> CompressionResult:
        """
        Compress text to reduce token usage.

        Args:
            text: Input text to compress
            aggressive: If True, apply more aggressive compression (line-level dedupe)

        Returns:
            CompressionResult with compressed text and metrics
        """
        original_tokens = estimate_tokens(text)

        # Step 1: Compress boilerplate
        compressed = self._compress_boilerplate(text)

        # Step 2: Split into blocks and deduplicate
        blocks = self._split_into_blocks(compressed, aggressive=aggressive)
        unique_blocks, removed = self._deduplicate_blocks(blocks)

        # Step 3: Rejoin
        join_char = "\n" if aggressive else "\n\n"
        compressed = join_char.join(unique_blocks)

        # Step 4: Additional aggressive compression
        if aggressive:
            # Remove excessive whitespace
            compressed = re.sub(r"\n{3,}", "\n\n", compressed)
            compressed = re.sub(r" {2,}", " ", compressed)
            # Shorten common phrases
            compressed = compressed.replace("```python", "```py")
            compressed = compressed.replace("```javascript", "```js")

        compressed_tokens = estimate_tokens(compressed)
        savings = (
            (original_tokens - compressed_tokens) / original_tokens * 100
            if original_tokens > 0
            else 0
        )

        # Update cumulative metrics
        self.metrics.update(original_tokens, compressed_tokens, len(removed))

        return CompressionResult(
            original_text=text,
            compressed_text=compressed,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            savings_percent=savings,
            removed_blocks=removed,
            fingerprint_cache_hits=len(self.fingerprint_cache),
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get cumulative token savings metrics."""
        return {
            "total_original_tokens": self.metrics.original_tokens,
            "total_compressed_tokens": self.metrics.compressed_tokens,
            "total_savings_tokens": self.metrics.savings_tokens,
            "savings_percent": round(self.metrics.savings_percent, 2),
            "blocks_removed": self.metrics.blocks_removed,
            "cache_size": len(self.fingerprint_cache),
            "timestamp": self.metrics.timestamp,
        }

    def reset_metrics(self):
        """Reset cumulative metrics."""
        self.metrics = TokenMetrics()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Global optimizer instance
_optimizer: Optional[ESMTokenOptimizer] = None


def get_optimizer() -> ESMTokenOptimizer:
    """Get or create global optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = ESMTokenOptimizer()
    return _optimizer


def compress_prompt(text: str, aggressive: bool = False) -> str:
    """Compress a prompt and return the compressed text."""
    result = get_optimizer().compress(text, aggressive)
    return result.compressed_text


def get_token_savings() -> Dict[str, Any]:
    """Get current token savings metrics."""
    return get_optimizer().get_metrics()


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ESM Token Optimizer")
    parser.add_argument("--input", type=str, help="Input file to compress")
    parser.add_argument("--output", type=str, help="Output file for compressed text")
    parser.add_argument(
        "--aggressive", action="store_true", help="Use aggressive compression"
    )
    parser.add_argument("--demo", action="store_true", help="Run demo with sample text")
    args = parser.parse_args()

    if args.demo:
        sample_text = """
# Important System Context

Please note that this is a very important document. It's important to note that we need to be careful here.

As mentioned earlier, the system uses a spectral analysis approach. As previously stated, this allows for efficient processing.

## Technical Details

In order to achieve the best results, we need to follow these steps:
1. First, due to the fact that the system is complex, we initialize carefully
2. At this point in time, we process the data
3. A large number of samples are analyzed

## Technical Details

In order to achieve the best results, we need to follow these steps:
1. First, due to the fact that the system is complex, we initialize carefully
2. At this point in time, we process the data
3. A large number of samples are analyzed

## Conclusion

In the event that errors occur, the system has the ability to recover automatically.
Prior to the final step, we validate all outputs.
"""

        optimizer = ESMTokenOptimizer()
        result = optimizer.compress(sample_text, aggressive=args.aggressive)

        print("=" * 60)
        print("ESM TOKEN OPTIMIZER DEMO")
        print("=" * 60)
        print(f"\nOriginal tokens: {result.original_tokens}")
        print(f"Compressed tokens: {result.compressed_tokens}")
        print(f"Savings: {result.savings_percent:.1f}%")
        print(f"Blocks removed: {len(result.removed_blocks)}")
        print("\n" + "-" * 60)
        print("COMPRESSED OUTPUT:")
        print("-" * 60)
        print(result.compressed_text)

    elif args.input:
        with open(args.input, "r") as f:
            text = f.read()

        optimizer = ESMTokenOptimizer()
        result = optimizer.compress(text, aggressive=args.aggressive)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result.compressed_text)
            print(f"Compressed output written to {args.output}")
        else:
            print(result.compressed_text)

        print(
            f"\n[INFO] Savings: {result.savings_percent:.1f}% ({result.original_tokens} -> {result.compressed_tokens} tokens)"
        )

    else:
        parser.print_help()

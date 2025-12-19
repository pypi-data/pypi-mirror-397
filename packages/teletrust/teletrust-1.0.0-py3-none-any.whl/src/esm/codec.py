"""
ESM Prime Gödel Codec
=====================
Implements reversible "Prime Gödel Codes" for:
1.  **Macro-States**: 343-state safety bins (Activity, Entropy, Pattern)
2.  **Micro-States**: 61-node graph activation masks

These codes provide a single, reversible integer representation of safety states,
enabling privacy-preserving audit logs and verifiable SLA compliance.

Mathematical Foundation:
------------------------
Relies on the Fundamental Theorem of Arithmetic (unique prime factorization).
Disjoint sets of primes are assigned to each dimension, ensuring bijectivity.

Safety-Critical Logic:
----------------------
This is NOT encryption. It is a structural encoding for transparency.
"""

from functools import reduce
from typing import Tuple, List, Dict
import math

# ==============================================================================
# 1. PRIME TABLES (DISJOINT SETS)
# ==============================================================================

# Macro-State Primes (for 7-bin discretization)
P_ACTIVITY = [2, 3, 5, 7, 11, 13, 17]
P_ENTROPY  = [19, 23, 29, 31, 37, 41, 43]
P_PATTERN  = [47, 53, 59, 61, 67, 71, 73]

# Reverse lookups
INV_ACTIVITY = {p: i for i, p in enumerate(P_ACTIVITY)}
INV_ENTROPY  = {p: i for i, p in enumerate(P_ENTROPY)}
INV_PATTERN  = {p: i for i, p in enumerate(P_PATTERN)}

# Micro-State Primes (for 61 nodes)
# First 61 primes (excluding those used above? No, can reuse if contexts are separate.
# But for purity, let's generate the first 61 primes dynamically or store them).
# Since these are two different CODECS, reusing primes is mathematically fine
# as long as we don't multiply macro_code * micro_code into one mega-integer
# (which would require disjoint sets).
# Let's generate them to be safe.

def generate_primes(n: int) -> List[int]:
    """Sieve of Eratosthenes to generate first n primes."""
    primes = []
    candidate = 2
    while len(primes) < n:
        is_prime = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes

# Pre-compute for 61 nodes
# We use a separate namespace for nodes, so standard primes 2, 3, 5... are fine.
P_NODES = generate_primes(61)
INV_NODES = {p: i for i, p in enumerate(P_NODES)}


# ==============================================================================
# 2. MACRO-STATE CODEC (343 States)
# ==============================================================================

class MacroStateCodec:
    """
    Encodes/Decodes (Activity, Entropy, Pattern) triplet -> Integer.
    Input bins must be in range [0, 6].
    """

    @staticmethod
    def encode(activity_bin: int, entropy_bin: int, pattern_bin: int) -> int:
        if not (0 <= activity_bin < 7 and 0 <= entropy_bin < 7 and 0 <= pattern_bin < 7):
            raise ValueError(f"Bins must be 0-6. Got ({activity_bin}, {entropy_bin}, {pattern_bin})")

        return (P_ACTIVITY[activity_bin] *
                P_ENTROPY[entropy_bin] *
                P_PATTERN[pattern_bin])

    @staticmethod
    def decode(code: int) -> Tuple[int, int, int]:
        if code <= 0:
            raise ValueError("Code must be positive integer")

        a, e, p = None, None, None

        # Factor out Activity
        for prime in P_ACTIVITY:
            if code % prime == 0:
                a = INV_ACTIVITY[prime]
                code //= prime
                break

        # Factor out Entropy
        for prime in P_ENTROPY:
            if code % prime == 0:
                e = INV_ENTROPY[prime]
                code //= prime
                break

        # Factor out Pattern
        for prime in P_PATTERN:
            if code % prime == 0:
                p = INV_PATTERN[prime]
                code //= prime
                break

        if None in (a, e, p) or code != 1:
             raise ValueError(f"Invalid macro code: residual={code}, found=({a},{e},{p})")

        return a, e, p


# ==============================================================================
# 3. MICRO-STATE CODEC (61 Nodes)
# ==============================================================================

class ESMPrimeStateCodec:
    """
    Encodes/Decodes 61-node boolean mask -> Integer.
    Enforces structural rules:
    1. Core nodes (0-20) match expected counts (usually always ON in theoretical model,
       but here we just encode the mask).
    2. 'Never 2/3 OFF' rule can be checked externally.
    """

    def __init__(self, n_nodes: int = 61):
        self.n_nodes = n_nodes
        self.primes = P_NODES[:n_nodes]
        if len(self.primes) != n_nodes:
            # Fallback if hardcoded list is short (it's not, we generated it)
            self.primes = generate_primes(n_nodes)

    def encode(self, node_mask: List[bool]) -> int:
        """
        Encode boolean mask to integer product.
        """
        if len(node_mask) != self.n_nodes:
            raise ValueError(f"Mask length {len(node_mask)} != {self.n_nodes}")

        product = 1
        for i, is_on in enumerate(node_mask):
            if is_on:
                product *= self.primes[i]
        return product

    def decode(self, code: int) -> List[bool]:
        """
        Decode integer product to boolean mask.
        NOTE: This creates a large integer (product of up to 61 primes).
        Python handles arbitrary precision integers automatically.
        """
        if code <= 0:
            raise ValueError("Code must be positive")

        mask = [False] * self.n_nodes
        remaining = code

        # Trial division
        for i, p in enumerate(self.primes):
            if remaining % p == 0:
                mask[i] = True
                remaining //= p
                # Check for repeated factors (invalid state)
                if remaining % p == 0:
                     raise ValueError(f"Invalid code: Repeated prime factor {p}")

            if remaining == 1:
                break

        if remaining != 1:
            raise ValueError(f"Code contains factors outside prime table: {remaining}")

        return mask

# ==============================================================================
# 4. AUDIT LOGGER
# ==============================================================================

import json
from datetime import datetime

class PrimeAuditLogger:
    """Helper to log prime codes for verifying attractor convergence."""

    @staticmethod
    def log_step(
        timestamp: float,
        step_idx: int,
        macro_bins: Tuple[int, int, int],
        node_mask: List[bool],
        file_path: str = "esm_audit.log"
    ):
        macro_code = MacroStateCodec.encode(*macro_bins)
        micro_codec = ESMPrimeStateCodec(len(node_mask))
        node_code = micro_codec.encode(node_mask)

        entry = {
            "ts": timestamp,
            "step": step_idx,
            "macro_code": macro_code,
            "node_code_hex": hex(node_code) # Store large int as hex
        }

        with open(file_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

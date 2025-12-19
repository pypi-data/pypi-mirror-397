"""
Grammar Matrix for Symbolic Spectral Grammar (SSG).

Tracks and validates state transitions (Markov chain order 1) with:
- Case sensitivity handling
- Memory usage caps for continuous learning
"""

from collections import defaultdict
from typing import Dict, Set, List, Iterable, Optional

class GrammarMemoryError(ValueError):
    """Raised when grammar memory limit is exceeded."""
    pass

class GrammarMatrix:
    """
    Learns and validates transitions between symbolic states.

    Structure:
        {
            "StateA": {"StateB", "StateC"},
            "StateB": {"StateA"}
        }
    """

    def __init__(self, case_sensitive: bool = False, max_transitions: int = 10000):
        """
        Initialize the Grammar Matrix.

        Parameters
        ----------
        case_sensitive : bool
            If False, all states are normalized to uppercase.
        max_transitions : int
            Maximum number of unique transitions (edges) to store.
            Prevents memory explosion during long training runs on noisy data.
        """
        self.matrix: Dict[str, Set[str]] = defaultdict(set)
        self.case_sensitive = case_sensitive
        self.max_transitions = max_transitions
        self._edge_count = 0

    def _normalize(self, state: str) -> str:
        """Normalize state based on case sensitivity settings."""
        return state if self.case_sensitive else state.upper()

    def train(self, sequence: Iterable[str]) -> None:
        """
        Learn transitions from a sequence of states.

        Parameters
        ----------
        sequence : Iterable[str]
            Stream of state tokens (e.g. ["Q", "T", "H", "T"]).
        """
        # Convert to list to handle indexing if iterable is a generator
        seq = list(sequence)

        if len(seq) < 2:
            return

        for i in range(len(seq) - 1):
            curr = self._normalize(str(seq[i]))
            next_state = self._normalize(str(seq[i+1]))

            if next_state not in self.matrix[curr]:
                # Check memory cap (Checklist 1.3 requirement)
                if self._edge_count >= self.max_transitions:
                    # Fail closed or just stop learning?
                    # For a "cap", we stop adding new edges but allow existing ones.
                    # We could raise an error, but logging/ignoring is safer for streams.
                    # Here we stop learning new patterns to preserve memory.
                    continue

                self.matrix[curr].add(next_state)
                self._edge_count += 1

    def is_valid_transition(self, current: str, next_state: str) -> bool:
        """
        Check if a transition is valid according to learned grammar.

        Returns
        -------
        bool
            True if transition exists, False otherwise.
            Note: Unknown states return False (Implicit strict mode).
        """
        curr = self._normalize(str(current))
        nxt = self._normalize(str(next_state))

        # If state unknown, transition is invalid
        if curr not in self.matrix:
            return False

        return nxt in self.matrix[curr]

    def to_dict(self) -> Dict[str, List[str]]:
        """Export grammar as JSON-serializable dictionary."""
        # Convert sets to lists and sort for deterministic output
        return {k: sorted(list(v)) for k, v in self.matrix.items()}

    def from_dict(self, data: Dict[str, List[str]]) -> None:
        """Load grammar from dictionary."""
        self.matrix.clear()
        self._edge_count = 0

        for k, v in data.items():
            norm_k = self._normalize(k)
            for target in v:
                if self._edge_count < self.max_transitions:
                    norm_target = self._normalize(target)
                    if norm_target not in self.matrix[norm_k]:
                        self.matrix[norm_k].add(norm_target)
                        self._edge_count += 1

#!/usr/bin/env python3
"""
Ephemeral Spectral Memory (ESM) Cell - Core Module
===================================================
Version: 1.0.0-locked
Author: Michael Ordon
License: PROPRIETARY - Trade Secret
SHA256: [computed at build]

61-node graph Laplacian system for multi-agent consensus tracking.
Uses spectral decomposition to detect disagreement patterns.

TRADE SECRET ELEMENTS:
1. Graph topology (4 center + 3×19 rails) - novel MOA architecture
2. Event-to-injection mapping for clinical/billing/policy domains
3. Mode interpretation schema (global, arm, rail, local)
4. Integration hooks for SSG (Spectral Structure Engine)

DO NOT DISTRIBUTE WITHOUT AUTHORIZATION.
"""

__version__ = "1.0.0"
__author__ = "Michael Ordon"
__license__ = "PROPRIETARY"

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
import json


def _compute_module_hash() -> str:
    """Compute hash of this module for integrity verification."""
    import inspect
    source = inspect.getsource(inspect.getmodule(_compute_module_hash))
    return hashlib.sha256(source.encode()).hexdigest()[:16]


MODULE_HASH = "COMPUTED_AT_RUNTIME"


@dataclass
class ESMConfig:
    """
    Configuration for Ephemeral Spectral Memory Cell.

    PROPRIETARY: These defaults are tuned for healthcare compliance domains.
    Changing them affects spectral response characteristics.
    """
    rail_len: int = 19              # 4 + 3*19 = 61 nodes total
    alpha: float = 0.05             # time-step * diffusion strength (forgetting rate)
    center_weight: float = 2.0      # hub/center connection strength
    rail_weight: float = 1.0        # along-rail connection strength
    master_to_rail_weight: float = 1.5  # connection from masters to first rail nodes

    # Threshold parameters (PROPRIETARY tuning)
    global_mode_threshold: float = 0.5      # Mode 0 amplitude triggering global alert
    arm_imbalance_threshold: float = 0.3    # Modes 1-3 for arm-level issues
    rail_conflict_threshold: float = 0.2    # Higher modes for local conflicts

    def to_dict(self) -> dict:
        return {
            "rail_len": self.rail_len,
            "alpha": self.alpha,
            "center_weight": self.center_weight,
            "rail_weight": self.rail_weight,
            "master_to_rail_weight": self.master_to_rail_weight,
            "global_mode_threshold": self.global_mode_threshold,
            "arm_imbalance_threshold": self.arm_imbalance_threshold,
            "rail_conflict_threshold": self.rail_conflict_threshold,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ESMConfig":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ESMSnapshot:
    """Immutable snapshot of ESM state for persistence/audit."""
    timestamp: str
    state_vector: List[float]
    mode_amplitudes: List[float]
    event_history: List[str]
    config_hash: str

    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp,
            "state_vector": self.state_vector,
            "mode_amplitudes": self.mode_amplitudes,
            "event_history": self.event_history,
            "config_hash": self.config_hash,
        })

    @classmethod
    def from_json(cls, s: str) -> "ESMSnapshot":
        d = json.loads(s)
        return cls(**d)


@dataclass
class ESMCell:
    """
    Ephemeral Spectral Memory Cell
    ==============================

    A 61-node graph implementing multi-agent consensus tracking via
    spectral decomposition of the graph Laplacian.

    Architecture:
    - Node 0: Global hub (system-wide state)
    - Nodes 1-3: Master A, B, C (agent heads)
    - Nodes 4-22: AB rail (A↔B cross-check channel)
    - Nodes 23-41: BC rail (B↔C cross-check channel)
    - Nodes 42-60: CA rail (C↔A cross-check channel)

    Dynamics:
        x_{t+1} = (I - α·L)·x_t + u_t

    Where L is the graph Laplacian, α controls forgetting, and u_t is
    the event injection vector.

    PROPRIETARY ELEMENTS:
    - Graph topology design (trade secret)
    - Event mapping schema (trade secret)
    - Threshold tuning (trade secret)
    """
    config: ESMConfig = field(default_factory=ESMConfig)

    # Internal state (filled at initialization)
    W: np.ndarray = field(init=False, repr=False)
    L: np.ndarray = field(init=False, repr=False)
    A_step: np.ndarray = field(init=False, repr=False)
    evals: np.ndarray = field(init=False, repr=False)
    evecs: np.ndarray = field(init=False, repr=False)
    x: np.ndarray = field(init=False, repr=False)
    event_map: Dict[str, np.ndarray] = field(init=False, repr=False)
    _event_history: List[str] = field(init=False, repr=False)
    _step_count: int = field(init=False, repr=False)

    def __post_init__(self):
        self._build_graph()
        self._build_dynamics()
        self._build_events()
        self._event_history = []
        self._step_count = 0
        self.reset()

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def n_nodes(self) -> int:
        """Total number of nodes in the graph."""
        return 4 + 3 * self.config.rail_len

    @property
    def idx_AB(self) -> np.ndarray:
        """Indices of AB rail nodes (A↔B cross-check)."""
        start = 4
        return np.arange(start, start + self.config.rail_len)

    @property
    def idx_BC(self) -> np.ndarray:
        """Indices of BC rail nodes (B↔C cross-check)."""
        start = 4 + self.config.rail_len
        return np.arange(start, start + self.config.rail_len)

    @property
    def idx_CA(self) -> np.ndarray:
        """Indices of CA rail nodes (C↔A cross-check)."""
        start = 4 + 2 * self.config.rail_len
        return np.arange(start, start + self.config.rail_len)

    @property
    def version(self) -> str:
        return __version__

    # =========================================================================
    # Graph Construction (PROPRIETARY TOPOLOGY)
    # =========================================================================

    def _build_graph(self):
        """
        Construct the weighted adjacency matrix W and Laplacian L.

        TRADE SECRET: The specific topology and weight distribution are
        optimized for healthcare compliance multi-agent scenarios.
        """
        n = self.n_nodes
        cfg = self.config

        W = np.zeros((n, n), dtype=np.float64)

        # Node indices
        GLOBAL = 0
        MA, MB, MC = 1, 2, 3  # Master agents: Clinical, Billing, Policy

        # Connect global hub to all masters (star topology center)
        for m in (MA, MB, MC):
            W[GLOBAL, m] = cfg.center_weight
            W[m, GLOBAL] = cfg.center_weight

        # Rail anchor nodes
        AB0 = self.idx_AB[0]
        BC0 = self.idx_BC[0]
        CA0 = self.idx_CA[0]

        # Master A (Clinical) connects to AB and CA rails
        W[MA, AB0] = cfg.master_to_rail_weight
        W[AB0, MA] = cfg.master_to_rail_weight
        W[MA, CA0] = cfg.master_to_rail_weight
        W[CA0, MA] = cfg.master_to_rail_weight

        # Master B (Billing) connects to AB and BC rails
        W[MB, AB0] = cfg.master_to_rail_weight
        W[AB0, MB] = cfg.master_to_rail_weight
        W[MB, BC0] = cfg.master_to_rail_weight
        W[BC0, MB] = cfg.master_to_rail_weight

        # Master C (Policy) connects to BC and CA rails
        W[MC, BC0] = cfg.master_to_rail_weight
        W[BC0, MC] = cfg.master_to_rail_weight
        W[MC, CA0] = cfg.master_to_rail_weight
        W[CA0, MC] = cfg.master_to_rail_weight

        # Connect each rail as a chain (information diffusion path)
        def connect_chain(indices: np.ndarray, weight: float):
            for i, j in zip(indices[:-1], indices[1:]):
                W[i, j] = weight
                W[j, i] = weight

        connect_chain(self.idx_AB, cfg.rail_weight)
        connect_chain(self.idx_BC, cfg.rail_weight)
        connect_chain(self.idx_CA, cfg.rail_weight)

        # Build Laplacian: L = D - W
        degrees = np.sum(W, axis=1)
        L = np.diag(degrees) - W

        self.W = W
        self.L = L

    # =========================================================================
    # Dynamics & Spectral Decomposition
    # =========================================================================

    def _build_dynamics(self):
        """
        Build discrete-time transition matrix and compute spectral decomposition.

        The eigenvalues of L determine forgetting rates per mode:
        - λ=0: constant mode (global baseline, never decays)
        - Small λ: slow modes (arm-level patterns, persist longer)
        - Large λ: fast modes (local fluctuations, decay quickly)
        """
        I = np.eye(self.n_nodes)
        self.A_step = I - self.config.alpha * self.L

        # Spectral decomposition (L is symmetric → use eigh)
        evals, evecs = np.linalg.eigh(self.L)
        self.evals = evals
        self.evecs = evecs

    # =========================================================================
    # Event Definitions (PROPRIETARY MAPPING)
    # =========================================================================

    def _build_events(self):
        """
        Define event-to-injection mappings.

        TRADE SECRET: These mappings encode domain knowledge about
        healthcare compliance disagreement patterns.
        """
        n = self.n_nodes

        def vec_for(nodes: List[int], magnitude: float = 1.0) -> np.ndarray:
            v = np.zeros(n, dtype=np.float64)
            v[nodes] = magnitude
            return v

        GLOBAL = 0
        MA, MB, MC = 1, 2, 3  # Clinical, Billing, Policy

        self.event_map = {
            # === CLINICAL ↔ BILLING (AB) EVENTS ===
            "AB_MINOR_DIFF": vec_for(
                [MA, MB, self.idx_AB[0], self.idx_AB[1]],
                magnitude=0.5
            ),
            "AB_MAJOR_DIFF": vec_for(
                [MA, MB] + self.idx_AB[:5].tolist(),
                magnitude=1.0
            ),
            "AB_CODE_MISMATCH": vec_for(
                [MA, MB] + self.idx_AB[:3].tolist(),
                magnitude=0.7
            ),

            # === BILLING ↔ POLICY (BC) EVENTS ===
            "BC_MINOR_DIFF": vec_for(
                [MB, MC, self.idx_BC[0], self.idx_BC[1]],
                magnitude=0.5
            ),
            "BC_POLICY_CONFLICT": vec_for(
                [MB, MC] + self.idx_BC[:5].tolist(),
                magnitude=1.0
            ),
            "BC_REIMBURSEMENT_FLAG": vec_for(
                [MB, MC] + self.idx_BC[:4].tolist(),
                magnitude=0.8
            ),

            # === CLINICAL ↔ POLICY (CA) EVENTS ===
            "CA_MINOR_DIFF": vec_for(
                [MA, MC, self.idx_CA[0], self.idx_CA[1]],
                magnitude=0.5
            ),
            "CA_POLICY_CONFLICT": vec_for(
                [MA, MC] + self.idx_CA[:5].tolist(),
                magnitude=1.0
            ),
            "CA_CONSENT_ISSUE": vec_for(
                [MA, MC] + self.idx_CA[:4].tolist(),
                magnitude=0.9
            ),

            # === GLOBAL EVENTS ===
            "ALL_GOOD": vec_for(
                [GLOBAL, MA, MB, MC],
                magnitude=0.2
            ),
            "ALL_DISAGREE": vec_for(
                [GLOBAL, MA, MB, MC] +
                self.idx_AB[:3].tolist() +
                self.idx_BC[:3].tolist() +
                self.idx_CA[:3].tolist(),
                magnitude=1.0
            ),
            "SYSTEM_RESET": vec_for(
                [GLOBAL],
                magnitude=0.1
            ),

            # === DOMAIN-SPECIFIC (Healthcare Compliance) ===
            "PHI_DETECTED": vec_for(
                [GLOBAL, MA] + self.idx_CA[:2].tolist(),
                magnitude=0.6
            ),
            "HIPAA_FLAG": vec_for(
                [MC] + self.idx_BC[:3].tolist() + self.idx_CA[:3].tolist(),
                magnitude=0.8
            ),
            "TELEHEALTH_CONSENT_MISSING": vec_for(
                [MA, MC] + self.idx_CA[:6].tolist(),
                magnitude=1.0
            ),
            "BILLING_CODE_INVALID": vec_for(
                [MB] + self.idx_AB[:4].tolist() + self.idx_BC[:4].tolist(),
                magnitude=0.9
            ),
        }

    # =========================================================================
    # Public API
    # =========================================================================

    def reset(self, value: float = 0.0):
        """Reset internal state to a constant value."""
        self.x = np.full(self.n_nodes, float(value), dtype=np.float64)
        self._event_history = []
        self._step_count = 0

    def apply_event(self, event: str) -> np.ndarray:
        """
        Get injection vector for a named event.

        Args:
            event: Event name from event_map

        Returns:
            Injection vector u (length n_nodes)

        Raises:
            ValueError: If event not found
        """
        if event not in self.event_map:
            available = list(self.event_map.keys())
            raise ValueError(f"Unknown event: {event}. Available: {available}")
        return self.event_map[event].copy()

    def step(self, u: np.ndarray, event_name: Optional[str] = None):
        """
        Advance one discrete-time step.

        Args:
            u: Injection vector (length n_nodes)
            event_name: Optional name for logging
        """
        self.x = self.A_step @ self.x + u
        self._step_count += 1
        if event_name:
            self._event_history.append(event_name)

    def step_event(self, event: str):
        """Convenience: apply named event and step."""
        u = self.apply_event(event)
        self.step(u, event_name=event)

    def project_to_modes(self) -> np.ndarray:
        """
        Project current state into eigenbasis of L.

        Returns:
            y = Q^T x where columns of Q are eigenvectors
        """
        return self.evecs.T @ self.x

    def get_mode_amplitudes(self) -> Dict[str, float]:
        """
        Get interpreted mode amplitudes.

        Returns dictionary with:
        - global_baseline: Mode 0 (constant mode)
        - arm_balance_A/B/C: Modes 1-3 (arm-level)
        - rail_activity: Sum of modes 4-10 (rail-level)
        - local_noise: Sum of higher modes (local fluctuations)
        """
        y = self.project_to_modes()

        return {
            "global_baseline": float(y[0]),
            "arm_balance_A": float(y[1]) if len(y) > 1 else 0.0,
            "arm_balance_B": float(y[2]) if len(y) > 2 else 0.0,
            "arm_balance_C": float(y[3]) if len(y) > 3 else 0.0,
            "rail_activity": float(np.sum(np.abs(y[4:11]))) if len(y) > 10 else 0.0,
            "local_noise": float(np.sum(np.abs(y[11:]))) if len(y) > 11 else 0.0,
        }

    def check_thresholds(self) -> Dict[str, bool]:
        """
        Check if any mode amplitudes exceed configured thresholds.

        Returns dictionary of threshold violations.
        """
        modes = self.get_mode_amplitudes()
        cfg = self.config

        return {
            "global_alert": abs(modes["global_baseline"]) > cfg.global_mode_threshold,
            "arm_A_imbalance": abs(modes["arm_balance_A"]) > cfg.arm_imbalance_threshold,
            "arm_B_imbalance": abs(modes["arm_balance_B"]) > cfg.arm_imbalance_threshold,
            "arm_C_imbalance": abs(modes["arm_balance_C"]) > cfg.arm_imbalance_threshold,
            "rail_conflict": modes["rail_activity"] > cfg.rail_conflict_threshold,
        }

    def mode_summary(self, k: int = 8) -> str:
        """Return text summary of first k modes."""
        y = self.project_to_modes()
        lines = []
        for i in range(min(k, len(self.evals))):
            lines.append(
                f"mode {i:2d}: λ={self.evals[i]:.4f}, amplitude={y[i]:+.4f}"
            )
        return "\n".join(lines)

    def snapshot(self) -> ESMSnapshot:
        """Create immutable snapshot of current state."""
        return ESMSnapshot(
            timestamp=datetime.utcnow().isoformat(),
            state_vector=self.x.tolist(),
            mode_amplitudes=self.project_to_modes().tolist(),
            event_history=self._event_history.copy(),
            config_hash=hashlib.sha256(
                json.dumps(self.config.to_dict()).encode()
            ).hexdigest()[:16],
        )

    def restore(self, snapshot: ESMSnapshot):
        """Restore state from snapshot."""
        self.x = np.array(snapshot.state_vector, dtype=np.float64)
        self._event_history = snapshot.event_history.copy()

    def get_available_events(self) -> List[str]:
        """Return list of all available event names."""
        return list(self.event_map.keys())

    def get_status(self) -> Dict:
        """Get comprehensive status dictionary."""
        modes = self.get_mode_amplitudes()
        thresholds = self.check_thresholds()

        return {
            "version": self.version,
            "n_nodes": self.n_nodes,
            "step_count": self._step_count,
            "mode_amplitudes": modes,
            "threshold_violations": thresholds,
            "any_violation": any(thresholds.values()),
            "recent_events": self._event_history[-10:],
        }


# =============================================================================
# Factory Functions
# =============================================================================

def create_esm_cell(
    rail_len: int = 19,
    alpha: float = 0.05,
    **kwargs
) -> ESMCell:
    """Factory function to create ESM cell with custom config."""
    config = ESMConfig(rail_len=rail_len, alpha=alpha, **kwargs)
    return ESMCell(config=config)


def create_healthcare_esm() -> ESMCell:
    """Create ESM cell pre-configured for healthcare compliance."""
    config = ESMConfig(
        rail_len=19,
        alpha=0.05,
        center_weight=2.0,
        rail_weight=1.0,
        master_to_rail_weight=1.5,
        global_mode_threshold=0.5,
        arm_imbalance_threshold=0.3,
        rail_conflict_threshold=0.2,
    )
    return ESMCell(config=config)


# =============================================================================
# Demo / Validation
# =============================================================================

if __name__ == "__main__":
    print(f"ESM Core v{__version__}")
    print(f"Module integrity: {_compute_module_hash()}")
    print("=" * 60)

    # Create cell
    esm = create_healthcare_esm()
    print(f"Nodes: {esm.n_nodes}")
    print(f"Available events: {len(esm.get_available_events())}")
    print(f"\nSmallest 10 eigenvalues:\n{esm.evals[:10]}")

    # Simulate sequence
    sequence = [
        "ALL_GOOD", "ALL_GOOD", "ALL_GOOD",
        "AB_MINOR_DIFF", "AB_MINOR_DIFF",
        "ALL_GOOD", "ALL_GOOD",
        "AB_MAJOR_DIFF", "AB_MAJOR_DIFF", "AB_MAJOR_DIFF",
        "BC_POLICY_CONFLICT", "BC_POLICY_CONFLICT",
        "ALL_GOOD", "ALL_GOOD", "ALL_GOOD", "ALL_GOOD", "ALL_GOOD",
    ]

    print("\n" + "=" * 60)
    print("Simulating event sequence...")
    print("=" * 60)

    for t, ev in enumerate(sequence):
        esm.step_event(ev)
        status = esm.get_status()

        print(f"\nStep {t:02d}: {ev}")
        print(f"  Global: {status['mode_amplitudes']['global_baseline']:+.4f}")
        print(f"  Arms A/B/C: {status['mode_amplitudes']['arm_balance_A']:+.4f} / "
              f"{status['mode_amplitudes']['arm_balance_B']:+.4f} / "
              f"{status['mode_amplitudes']['arm_balance_C']:+.4f}")
        print(f"  Rail activity: {status['mode_amplitudes']['rail_activity']:.4f}")

        if status['any_violation']:
            violations = [k for k, v in status['threshold_violations'].items() if v]
            print(f"  ⚠️  VIOLATIONS: {violations}")

    # Final snapshot
    print("\n" + "=" * 60)
    print("Final mode summary:")
    print(esm.mode_summary(k=8))

    snapshot = esm.snapshot()
    print(f"\nSnapshot created: {snapshot.timestamp}")
    print(f"Config hash: {snapshot.config_hash}")

"""
Ephemeral Spectral Memory (ESM) Package
=======================================

PROPRIETARY - Trade Secret
Author: Michael Ordon

Components:
- ESMCell: 61-node graph Laplacian consensus tracker
- ESMConfig: Configuration dataclass
- ESMSnapshot: Immutable state snapshot for persistence
"""

from src.esm.core import (
    ESMCell,
    ESMConfig,
    ESMSnapshot,
    create_esm_cell,
    create_healthcare_esm,
)

__all__ = [
    "ESMCell",
    "ESMConfig",
    "ESMSnapshot",
    "create_esm_cell",
    "create_healthcare_esm",
]

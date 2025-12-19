from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Optional

import numpy as np
from sklearn.neighbors import NearestNeighbors


@dataclass
class MOAConfig:
    """
    Configuration for Magnetic Outlier Agent.

    Attributes
    ----------
    k : int
        Neighborhood size for the k-NN graph (typical range: 10–20).
    lambda_ : float
        Threshold multiplier controlling the strictness of outlier detection. A
        larger value yields fewer outliers by requiring higher deviation from
        the mean score (μ + λ·σ).
    epsilon : float
        Small constant to avoid division-by-zero when computing statistics.
    """

    k: int = 15
    lambda_: float = 1.5
    epsilon: float = 1e-6


@dataclass
class OutlierResult:
    """
    Encapsulates the result for a single data point after outlier detection.

    Attributes
    ----------
    index : int
        Original index of the point in the input data.
    score : float
        Composite outlier score for this point.
    is_outlier : bool
        Flag indicating whether the point exceeds the outlier threshold.
    z_centroid : float
        Z-score of the distance to the global centroid.
    z_density : float
        Z-score of the local density measure (negative mean neighbor distance).
    z_clustering : float
        Z-score of the local clustering coefficient.
    neighbors : List[int]
        Indices of the k nearest neighbors used to compute local metrics.
    """

    index: int
    score: float
    is_outlier: bool
    z_centroid: float
    z_density: float
    z_clustering: float
    neighbors: List[int]


class MOAError(Exception):
    """Exception raised for errors in the Magnetic Outlier Agent."""
    pass


class MagneticOutlierAgent:
    """
    Magnetic Outlier Agent (Python implementation).

    This agent computes geometric outlier scores for a set of embedding vectors.
    It constructs a k-nearest neighbor (k-NN) graph, calculates three per-point
    metrics (distance from global centroid, local density, and clustering
    coefficient), normalizes them via z-scores, and combines them into a
    composite score. Points whose scores exceed μ + λ·σ are flagged as outliers.

    Parameters
    ----------
    config : MOAConfig, optional
        Configuration for the agent. If `None`, default settings are used.
    """

    def __init__(self, config: Optional[MOAConfig] = None) -> None:
        self.config = config or MOAConfig()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def detect_outliers(
        self,
        embeddings: Sequence[Sequence[float]],
        *,
        metric: str = "euclidean",
    ) -> List[OutlierResult]:
        """
        Detect outliers in a set of embedding vectors.

        Parameters
        ----------
        embeddings : Sequence[Sequence[float]]
            A 2D sequence (e.g., list of lists or NumPy array) where each
            sub-sequence is a point in d-dimensional space.
        metric : str, optional
            Distance metric used for nearest-neighbor search. Defaults to
            "euclidean".

        Returns
        -------
        List[OutlierResult]
            A list of results for each point, sorted by descending composite
            outlier score.

        Raises
        ------
        MOAError
            If there are insufficient points relative to k, or if the
            embeddings do not form a 2D array.
        """
        X = self._to_numpy(embeddings)
        n_samples, _ = X.shape

        if n_samples <= self.config.k + 1:
            raise MOAError(
                f"Too few points for k={self.config.k}: got N={n_samples}"
            )

        # Step 1: compute k-NN indices (excluding self)
        neighbors = self._knn_indices(X, k=self.config.k, metric=metric)

        # Step 2: compute global centroid of the embeddings
        centroid = X.mean(axis=0)

        # Step 3: compute per-point metrics
        d_centroid = self._centroid_distances(X, centroid)
        density_score = self._local_density_score(X, neighbors)
        clustering = self._local_clustering_coeff(neighbors)

        # Step 4: normalize metrics via z-scores
        z_centroid = self._z_score(d_centroid)
        z_density = self._z_score(density_score)
        z_clustering = self._z_score(clustering)

        # Step 5: compute composite score
        scores = z_centroid - z_density - z_clustering

        # Step 6: determine outlier threshold
        mean_score = float(scores.mean())
        std_score = float(scores.std())
        threshold = (
            float("inf")
            if std_score < self.config.epsilon
            else mean_score + self.config.lambda_ * std_score
        )

        # Step 7: assemble results
        results: List[OutlierResult] = []
        for idx in range(n_samples):
            results.append(
                OutlierResult(
                    index=idx,
                    score=float(scores[idx]),
                    is_outlier=bool(scores[idx] > threshold),
                    z_centroid=float(z_centroid[idx]),
                    z_density=float(z_density[idx]),
                    z_clustering=float(z_clustering[idx]),
                    neighbors=list(map(int, neighbors[idx].tolist())),
                )
            )

        # Step 8: return results sorted by descending score
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    # ------------------------------------------------------------------
    # Internal helper functions
    # ------------------------------------------------------------------
    @staticmethod
    def _to_numpy(embeddings: Sequence[Sequence[float]]) -> np.ndarray:
        """Convert an arbitrary 2D sequence into a NumPy array."""
        X = np.asarray(embeddings, dtype=np.float32)
        if X.ndim != 2:
            raise MOAError(f"Expected a 2D embeddings array, got shape {X.shape}")
        return X

    @staticmethod
    def _z_score(x: np.ndarray, eps: float = 1e-8) -> np.ndarray:
        """Compute the z-scores of an array."""
        mean = x.mean()
        std = x.std()
        if std < eps:
            return np.zeros_like(x, dtype=np.float64)
        return (x - mean) / std

    def _knn_indices(
        self, X: np.ndarray, k: int, metric: str = "euclidean"
    ) -> np.ndarray:
        """
        Compute the indices of the k nearest neighbors for each point.

        The first neighbor returned by scikit-learn is always the point itself.
        This method discards the self-index, returning an array of shape
        (n_samples, k).
        """
        n_samples = X.shape[0]
        if k >= n_samples:
            raise MOAError(f"k={k} must be less than the number of samples {n_samples}")

        nn = NearestNeighbors(
            n_neighbors=k + 1,
            metric=metric,
            algorithm="auto",
            n_jobs=-1,
        )
        nn.fit(X)
        _, indices = nn.kneighbors(X, return_distance=True)
        return indices[:, 1:]

    @staticmethod
    def _centroid_distances(X: np.ndarray, centroid: np.ndarray) -> np.ndarray:
        """
        Compute the Euclidean distance of each point from the global centroid.
        """
        diff = X - centroid
        return np.linalg.norm(diff, axis=1).astype(np.float64)

    def _local_density_score(
        self, X: np.ndarray, neighbors: np.ndarray
    ) -> np.ndarray:
        """
        Compute a local density score for each point.

        The density score is defined as the negative mean distance to the k
        neighbors. A more negative value indicates a sparser neighborhood.
        """
        n_samples, _ = X.shape
        k = neighbors.shape[1]
        density = np.empty(n_samples, dtype=np.float64)

        for i in range(n_samples):
            nbr_idx = neighbors[i]
            nbr_vecs = X[nbr_idx]  # shape (k, d)
            diff = nbr_vecs - X[i]
            dists = np.linalg.norm(diff, axis=1)
            density[i] = -float(dists.mean())
        return density

    @staticmethod
    def _local_clustering_coeff(neighbors: np.ndarray) -> np.ndarray:
        """
        Estimate a local clustering coefficient for each point based on its
        neighbor list.

        For each point i, the coefficient is the fraction of unordered pairs of
        neighbors that are themselves neighbors of each other. This is a simple
        approximation using only the k-NN lists (it does not construct a full
        graph).
        """
        n_samples, k = neighbors.shape
        coeffs = np.zeros(n_samples, dtype=np.float64)

        # Precompute neighbor sets for constant-time membership checks
        neighbor_sets = [set(neighbors[i].tolist()) for i in range(n_samples)]

        for i in range(n_samples):
            if k < 2:
                coeffs[i] = 0.0
                continue

            possible_edges = k * (k - 1) / 2
            actual_edges = 0
            nbrs = neighbors[i]

            # Count edges among neighbors (each pair counted once)
            for a in range(k):
                u = int(nbrs[a])
                neigh_u = neighbor_sets[u]
                for b in range(a + 1, k):
                    v = int(nbrs[b])
                    if v in neigh_u:
                        actual_edges += 1
            coeffs[i] = actual_edges / possible_edges if possible_edges > 0 else 0.0
        return coeffs

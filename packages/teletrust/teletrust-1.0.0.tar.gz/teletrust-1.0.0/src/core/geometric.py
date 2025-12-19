"""
Geometric Outlier Detection: Stage I of Magnetic Outlier Agent (MOA)

.. deprecated:: 1.1.0
   This module is DEPRECATED. Use `magnetic_outlier_agent.py` instead.
   `MagneticOutlierAgent` provides the same functionality with better API.

Multi-metric anomaly detection combining:
- Centroid distance (global positioning)
- Local density (neighborhood analysis)
- Clustering coefficient (graph cohesion)

Author: Michael Ordon (grzywajk-beep)
License: BSL 1.1
"""

import warnings
warnings.warn(
    "geometric.py is deprecated. Use magnetic_outlier_agent.py instead.",
    DeprecationWarning,
    stacklevel=2
)

import numpy as np
from typing import Tuple, List, Optional
from sklearn.neighbors import NearestNeighbors


class GeometricDetector:
    """
    Stage I geometric outlier detection for MOA.

    Combines three metrics:
    1. d_i: Distance to centroid (global anomaly)
    2. δ_i: Local density (neighborhood sparsity)
    3. κ_i: Clustering coefficient (graph cohesion)

    Composite score: Z(d_i) - Z(δ_i) - Z(κ_i)
    Higher scores indicate stronger outliers.
    """

    def __init__(
        self,
        k_neighbors: int = 15,
        lambda_threshold: float = 1.5,
        metric: str = 'euclidean'
    ) -> None:
        """
        Initialize GeometricDetector.

        Args:
            k_neighbors: Number of nearest neighbors for density/clustering
            lambda_threshold: Std deviations above mean for outlier flagging
            metric: Distance metric ('euclidean', 'cosine', 'manhattan')

        Raises:
            ValueError: If parameters invalid
        """
        if k_neighbors < 2:
            raise ValueError("k_neighbors must be >= 2")
        if lambda_threshold <= 0:
            raise ValueError("lambda_threshold must be > 0")
        if metric not in ['euclidean', 'cosine', 'manhattan']:
            raise ValueError(f"Unsupported metric: {metric}")

        self.k_neighbors = k_neighbors
        self.lambda_threshold = lambda_threshold
        self.metric = metric

    def _validate_embeddings(self, embeddings: np.ndarray) -> None:
        """
        Validate input embeddings.

        Args:
            embeddings: Input array (N x d)

        Raises:
            ValueError: On invalid input
        """
        if not isinstance(embeddings, np.ndarray):
            raise ValueError("Embeddings must be numpy array")

        if embeddings.ndim != 2:
            raise ValueError(f"Expected 2D array, got {embeddings.ndim}D")

        N, d = embeddings.shape

        if N < 10:
            raise ValueError(f"Need at least 10 samples, got {N}")

        if d < 2:
            raise ValueError(f"Need at least 2 dimensions, got {d}")

        if self.k_neighbors >= N:
            warnings.warn(
                f"k_neighbors ({self.k_neighbors}) >= N ({N}), "
                f"reducing to {N-1}",
                UserWarning
            )
            self.k_neighbors = N - 1

        if not np.all(np.isfinite(embeddings)):
            raise ValueError("Embeddings contain inf/NaN values")

    def _compute_centroid_distances(
        self,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute distance of each point to centroid.

        Args:
            embeddings: Input array (N x d)

        Returns:
            Array of distances (N,)
        """
        centroid = np.mean(embeddings, axis=0)

        if self.metric == 'euclidean':
            distances = np.linalg.norm(embeddings - centroid, axis=1)
        elif self.metric == 'cosine':
            # Cosine distance = 1 - cosine similarity
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            centroid_norm = np.linalg.norm(centroid)
            similarities = (embeddings @ centroid) / (norms.flatten() * centroid_norm + 1e-8)
            distances = 1 - similarities
        else:  # manhattan
            distances = np.sum(np.abs(embeddings - centroid), axis=1)

        return distances

    def _compute_local_density(
        self,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute local density using k-NN.

        δ_i = k / Σ(dist to k neighbors)
        Higher δ means denser neighborhood.

        Args:
            embeddings: Input array (N x d)

        Returns:
            Array of densities (N,)
        """
        nbrs = NearestNeighbors(
            n_neighbors=self.k_neighbors + 1,  # +1 for self
            metric=self.metric
        ).fit(embeddings)

        distances, _ = nbrs.kneighbors(embeddings)

        # Exclude self (first neighbor)
        neighbor_dists = distances[:, 1:]

        # Sum of distances to k neighbors
        sum_dists = np.sum(neighbor_dists, axis=1) + 1e-8

        # Density = k / sum_dists
        densities = self.k_neighbors / sum_dists

        return densities

    def _compute_clustering_coefficient(
        self,
        embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute local clustering coefficient.

        κ_i = (# of edges between neighbors) / (# possible edges)

        Args:
            embeddings: Input array (N x d)

        Returns:
            Array of clustering coefficients (N,)
        """
        N = len(embeddings)

        nbrs = NearestNeighbors(
            n_neighbors=self.k_neighbors + 1,
            metric=self.metric
        ).fit(embeddings)

        distances, indices = nbrs.kneighbors(embeddings)

        coefficients = np.zeros(N)

        for i in range(N):
            # Get k nearest neighbors (excluding self)
            neighbors = indices[i, 1:]
            neighbor_dists = distances[i, 1:]

            # Max distance to consider edge
            max_dist = neighbor_dists[-1] * 1.2

            # Count edges between neighbors
            edges = 0
            possible = 0

            for a in range(len(neighbors)):
                for b in range(a + 1, len(neighbors)):
                    possible += 1

                    # Check if edge exists
                    idx_a, idx_b = neighbors[a], neighbors[b]
                    dist = np.linalg.norm(
                        embeddings[idx_a] - embeddings[idx_b]
                    )

                    if dist < max_dist:
                        edges += 1

            coefficients[i] = edges / possible if possible > 0 else 0

        return coefficients

    def _z_normalize(self, values: np.ndarray) -> np.ndarray:
        """
        Z-score normalization.

        Args:
            values: Input array

        Returns:
            Normalized array
        """
        mean = np.mean(values)
        std = np.std(values) + 1e-8
        return (values - mean) / std

    def detect(
        self,
        embeddings: np.ndarray,
        return_components: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, Optional[dict]]:
        """
        Detect outliers using geometric multi-metric approach.

        Args:
            embeddings: Input array (N x d)
            return_components: If True, return individual metric scores

        Returns:
            Tuple of:
            - scores: Composite outlier scores (N,)
            - outlier_mask: Boolean mask of outliers (N,)
            - components: Dict of individual metrics (if return_components=True)

        Raises:
            ValueError: On invalid input
        """
        self._validate_embeddings(embeddings)

        # Compute individual metrics
        d_i = self._compute_centroid_distances(embeddings)
        delta_i = self._compute_local_density(embeddings)
        kappa_i = self._compute_clustering_coefficient(embeddings)

        # Z-normalize
        z_d = self._z_normalize(d_i)
        z_delta = self._z_normalize(delta_i)
        z_kappa = self._z_normalize(kappa_i)

        # Composite score
        # High score = far from centroid + low density + low clustering
        scores = z_d - z_delta - z_kappa

        # Threshold
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        threshold = mean_score + self.lambda_threshold * std_score

        outlier_mask = scores > threshold

        components = None
        if return_components:
            components = {
                'centroid_distance': d_i,
                'local_density': delta_i,
                'clustering_coefficient': kappa_i,
                'z_centroid_distance': z_d,
                'z_local_density': z_delta,
                'z_clustering_coefficient': z_kappa,
                'threshold': threshold
            }

        return scores, outlier_mask, components

    def explain_outlier(
        self,
        idx: int,
        embeddings: np.ndarray,
        scores: np.ndarray,
        components: dict
    ) -> str:
        """
        Generate human-readable explanation for why a point is an outlier.

        Args:
            idx: Index of point to explain
            embeddings: Original embeddings
            scores: Outlier scores from detect()
            components: Component dict from detect(return_components=True)

        Returns:
            Explanation string
        """
        if components is None:
            raise ValueError("Must call detect() with return_components=True first")

        d_i = components['centroid_distance'][idx]
        delta_i = components['local_density'][idx]
        kappa_i = components['clustering_coefficient'][idx]
        score = scores[idx]

        explanation = f"Point {idx} Outlier Analysis:\n"
        explanation += f"  Composite Score: {score:.3f}\n"
        explanation += f"  Centroid Distance: {d_i:.3f} "
        explanation += f"({'far' if d_i > np.median(components['centroid_distance']) else 'near'})\n"
        explanation += f"  Local Density: {delta_i:.3f} "
        explanation += f"({'sparse' if delta_i < np.median(components['local_density']) else 'dense'})\n"
        explanation += f"  Clustering Coeff: {kappa_i:.3f} "
        explanation += f"({'isolated' if kappa_i < np.median(components['clustering_coefficient']) else 'cohesive'})\n"

        # Determine primary reason
        z_d = components['z_centroid_distance'][idx]
        z_delta = components['z_local_density'][idx]
        z_kappa = components['z_clustering_coefficient'][idx]

        reasons = []
        if z_d > 1.5:
            reasons.append("far from centroid")
        if z_delta < -1.5:
            reasons.append("low neighborhood density")
        if z_kappa < -1.5:
            reasons.append("weak clustering")

        if reasons:
            explanation += f"\n  Primary Factors: {', '.join(reasons)}"

        return explanation


def detect_outliers(embeddings: np.ndarray, threshold: float = 1.5, k: int = 15) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convenience wrapper for GeometricDetector.

    Args:
        embeddings: Input vectors
        threshold: Z-score threshold (default 1.5)
        k: Neighbors (default 15)

    Returns:
        (scores, mask)
    """
    # Ensure embeddings are numpy array
    if not isinstance(embeddings, np.ndarray):
        embeddings = np.array(embeddings)

    detector = GeometricDetector(k_neighbors=k, lambda_threshold=threshold)
    scores, mask, _ = detector.detect(embeddings)
    return scores, mask


# Example usage
if __name__ == "__main__":
    # Generate synthetic data
    np.random.seed(42)

    # Normal cluster
    normal = np.random.randn(100, 10) * 0.5

    # Outliers (far from origin)
    outliers = np.random.randn(10, 10) * 2 + 5

    embeddings = np.vstack([normal, outliers])

    # Detect
    detector = GeometricDetector(k_neighbors=15, lambda_threshold=1.5)
    scores, mask, components = detector.detect(
        embeddings,
        return_components=True
    )

    print(f"Detected {np.sum(mask)} outliers out of {len(embeddings)} points")
    print(f"Outlier indices: {np.where(mask)[0]}")

    # Explain first outlier
    if np.any(mask):
        first_outlier = np.where(mask)[0][0]
        explanation = detector.explain_outlier(
            first_outlier,
            embeddings,
            scores,
            components
        )
        print(f"\n{explanation}")

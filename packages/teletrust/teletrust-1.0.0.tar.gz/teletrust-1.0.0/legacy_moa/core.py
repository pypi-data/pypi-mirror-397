import numpy as np
from sklearn.base import BaseEstimator, OutlierMixin
from sklearn.neighbors import NearestNeighbors

class MagneticOutlierAgent(BaseEstimator, OutlierMixin):
    def __init__(self,
                 n_neighbors=20,
                 metric="cosine",
                 n_jobs=None):
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.n_jobs = n_jobs

    def fit(self, X, y=None):
        X = np.asarray(X)
        self._nn = NearestNeighbors(
            n_neighbors=self.n_neighbors,
            metric=self.metric,
            n_jobs=self.n_jobs,
        )
        self._nn.fit(X)
        self._X_fit = X
        return self

    def _triple_metric_scores(self, distances):
        # v1: keep it stupid-simple – you can fancy it up later.
        # Example:
        # - m1: mean distance to neighbors
        # - m2: max distance
        # - m3: variance of distances
        m1 = distances.mean(axis=1)
        m2 = distances.max(axis=1)
        m3 = distances.var(axis=1)
        # simple normalized combo
        raw = m1 + m2 + m3
        return raw

    def score_samples(self, X):
        X = np.asarray(X)
        distances, _ = self._nn.kneighbors(X, n_neighbors=self.n_neighbors)
        scores = self._triple_metric_scores(distances)
        # Convention: higher = more normal; convert to anomaly-style if needed
        return -scores  # more negative = more anomalous

    def fit_predict(self, X, y=None):
        self.fit(X)
        scores = self.score_samples(X)
        # simple threshold at median
        thresh = np.median(scores)
        labels = (scores < thresh).astype(int)  # 1 = outlier
        return labels

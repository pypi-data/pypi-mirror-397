import numpy as np
from moa import MagneticOutlierAgent

def test_basic_fit_predict():
    X = np.random.randn(100, 8)
    moa = MagneticOutlierAgent(n_neighbors=10)
    labels = moa.fit_predict(X)
    assert labels.shape == (100,)

"""
SSG 192-Dimension Fingerprint Runtime API
==========================================
Exposes the SSG spectral fingerprint as a high-level runtime service.

192 dimensions = 3 series (prime, even, odd_composite) × 64 frequency bins
"""

from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime

from src.core.ssg import compute_ssg_fingerprint, encode_text_to_symbols, compute_symbol_entropy


class SSGFingerprintRuntime:
    """
    High-level runtime for SSG 192-dimension fingerprinting.
    
    Usage:
        runtime = SSGFingerprintRuntime()
        result = runtime.fingerprint("Your text here")
        # result["vector"] is a 192-dim numpy array
    """
    
    N_BINS = 64  # 64 bins × 3 series = 192 dimensions
    
    def __init__(self, store=None):
        """
        Initialize the SSG runtime.
        
        Args:
            store: Optional ESMBaselineStore for persistence
        """
        self.store = store
    
    def fingerprint(
        self,
        text: str,
        session_id: Optional[str] = None,
        persist: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a 192-dimension SSG fingerprint for the given text.
        
        Args:
            text: Input text to fingerprint
            session_id: Optional session ID for tracking
            persist: If True and store is configured, save to baseline store
            metadata: Optional metadata to store
            
        Returns:
            dict with keys:
                - vector: 192-dim numpy array
                - entropy: Shannon entropy of input
                - dimensions: 192
                - timestamp: ISO timestamp
                - session_id: if provided
                - hash: if persisted
        """
        # Compute fingerprint
        vector = compute_ssg_fingerprint(text, n_bins=self.N_BINS)
        
        # Compute entropy for quality assessment
        symbols = encode_text_to_symbols(text)
        entropy = compute_symbol_entropy(symbols)
        
        result = {
            "vector": vector,
            "dimensions": len(vector),
            "entropy": float(entropy),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if session_id:
            result["session_id"] = session_id
        
        # Persist if requested and store available
        if persist and self.store and session_id:
            store_result = self.store.store(
                session_id=session_id,
                fingerprint=vector.tolist(),
                metadata=metadata or {"entropy": entropy}
            )
            result["hash"] = store_result["curr_hash"]
            result["prev_hash"] = store_result["prev_hash"]
        
        return result
    
    def compare(
        self,
        text_a: str,
        text_b: str,
    ) -> Dict[str, Any]:
        """
        Compare two texts and return similarity metrics.
        
        Args:
            text_a: First text
            text_b: Second text
            
        Returns:
            dict with similarity score and component breakdown
        """
        fp_a = compute_ssg_fingerprint(text_a, n_bins=self.N_BINS)
        fp_b = compute_ssg_fingerprint(text_b, n_bins=self.N_BINS)
        
        # Cosine similarity
        norm_a = np.linalg.norm(fp_a)
        norm_b = np.linalg.norm(fp_b)
        
        if norm_a == 0 or norm_b == 0:
            cosine_sim = 0.0
        else:
            cosine_sim = float(np.dot(fp_a, fp_b) / (norm_a * norm_b))
        
        # Euclidean distance (normalized)
        euclidean_dist = float(np.linalg.norm(fp_a - fp_b))
        
        # Component breakdown (64 bins each)
        prime_sim = self._component_similarity(fp_a[:64], fp_b[:64])
        even_sim = self._component_similarity(fp_a[64:128], fp_b[64:128])
        odd_sim = self._component_similarity(fp_a[128:], fp_b[128:])
        
        return {
            "cosine_similarity": cosine_sim,
            "euclidean_distance": euclidean_dist,
            "components": {
                "prime": prime_sim,
                "even": even_sim,
                "odd_composite": odd_sim,
            },
            "match": cosine_sim > 0.85,  # Threshold for "same author"
        }
    
    def _component_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity for a single component."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
    
    def batch_fingerprint(
        self,
        texts: List[str],
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fingerprint multiple texts efficiently.
        
        Args:
            texts: List of texts to fingerprint
            session_id: Optional shared session ID
            
        Returns:
            List of fingerprint results
        """
        return [
            self.fingerprint(text, session_id=session_id)
            for text in texts
        ]


# Convenience function
def get_ssg_fingerprint(text: str) -> np.ndarray:
    """
    Quick 192-dimension fingerprint extraction.
    
    Args:
        text: Input text
        
    Returns:
        192-dimension numpy array
    """
    return compute_ssg_fingerprint(text, n_bins=64)


if __name__ == "__main__":
    # Test the runtime
    runtime = SSGFingerprintRuntime()
    
    # Test fingerprint
    result = runtime.fingerprint("The quick brown fox jumps over the lazy dog.")
    print(f"Dimensions: {result['dimensions']}")
    print(f"Entropy: {result['entropy']:.2f} bits")
    print(f"Vector (first 10): {result['vector'][:10]}")
    
    # Test comparison
    text1 = "The patient presents with symptoms of anxiety and depression."
    text2 = "A patient is showing signs of anxiety along with depressive symptoms."
    text3 = "Hello world, this is a completely different sentence structure."
    
    print("\n--- Comparison Tests ---")
    sim1 = runtime.compare(text1, text2)
    print(f"Similar texts: cosine={sim1['cosine_similarity']:.3f}, match={sim1['match']}")
    
    sim2 = runtime.compare(text1, text3)
    print(f"Different texts: cosine={sim2['cosine_similarity']:.3f}, match={sim2['match']}")

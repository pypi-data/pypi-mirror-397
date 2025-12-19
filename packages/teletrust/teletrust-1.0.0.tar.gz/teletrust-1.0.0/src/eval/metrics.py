"""
Eval Metrics - Scoring Functions
=================================
Individual metric calculations for hallucination detection.
"""

from typing import List, Tuple


def calculate_faithfulness(response: str, source_document: str) -> Tuple[float, List[str]]:
    """
    Calculate faithfulness score: what % of claims are grounded in source.

    Args:
        response: LLM response text
        source_document: Source document to check against

    Returns:
        (faithfulness_score, list of ungrounded claims)
    """
    # Simple n-gram overlap approach
    # Production would use NLI model or embedding similarity

    response_sentences = [s.strip() for s in response.split(".") if s.strip()]
    source_lower = source_document.lower()

    grounded = []
    ungrounded = []

    for sentence in response_sentences:
        # Check if key terms from sentence appear in source
        words = sentence.lower().split()
        key_words = [w for w in words if len(w) > 4]  # Skip short words

        if not key_words:
            grounded.append(sentence)
            continue

        matches = sum(1 for w in key_words if w in source_lower)
        overlap = matches / len(key_words) if key_words else 0

        if overlap >= 0.5:
            grounded.append(sentence)
        else:
            ungrounded.append(sentence)

    total = len(response_sentences)
    score = len(grounded) / total if total > 0 else 1.0

    return score, ungrounded


def calculate_citation_validity(
    citations: List[dict], reference_db: dict
) -> Tuple[float, List[str]]:
    """
    Calculate citation validity: what % of citations are correct.

    Args:
        citations: List of citation objects from response
        reference_db: Database of valid references

    Returns:
        (validity_score, list of invalid citations)
    """
    if not citations:
        return 1.0, []  # No citations to validate

    valid = []
    invalid = []

    for citation in citations:
        cite_id = citation.get("id", "")
        cite_text = citation.get("text", "")

        # Check if citation exists in reference DB
        if cite_id in reference_db:
            ref = reference_db[cite_id]
            # Check if cited text actually appears in reference
            if cite_text.lower() in ref.get("content", "").lower():
                valid.append(cite_id)
            else:
                invalid.append(f"{cite_id}: text not found in source")
        else:
            invalid.append(f"{cite_id}: citation does not exist")

    score = len(valid) / len(citations)
    return score, invalid


def calculate_variance(responses: List[str]) -> Tuple[float, bool]:
    """
    Calculate variance across multiple runs of same prompt.

    Args:
        responses: List of responses from same prompt with different seeds

    Returns:
        (variance_score, is_stable)
    """
    if len(responses) < 2:
        return 0.0, True

    # Calculate similarity using word overlap (Jaccard index)

    # Calculate Jaccard similarity between response pairs
    similarities = []
    for i in range(len(responses)):
        for j in range(i + 1, len(responses)):
            words_i = set(responses[i].lower().split())
            words_j = set(responses[j].lower().split())

            intersection = words_i & words_j
            union = words_i | words_j

            jaccard = len(intersection) / len(union) if union else 1.0
            similarities.append(jaccard)

    avg_similarity = sum(similarities) / len(similarities) if similarities else 1.0
    variance = 1 - avg_similarity

    # Stable if variance < 5%
    is_stable = variance < 0.05

    return variance, is_stable

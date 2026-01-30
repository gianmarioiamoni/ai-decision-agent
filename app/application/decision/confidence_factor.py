# app/application/decision/confidence_factor.py

# This file contains the confidence factor for historical decisions.
# It is used to compute the confidence contribution from historical decisions.

from typing import List
from app.application.decision.historical_evidence import (
    HistoricalDecisionEvidence,
)


MAX_HISTORICAL_CONFIDENCE = 0.3


def historical_confidence_factor(
    evidences: List[HistoricalDecisionEvidence],
) -> float:
    #
    # Computes the confidence contribution from historical decisions.
    #
    # Args:
    #     evidences: List of HistoricalDecisionEvidence
    #
    # Returns:
    #     float: Confidence contribution from historical decisions
    #
    #
    # Rules:
    # - Uses average similarity
    # - Scaled by decision confidence
    # - Capped to avoid dominance
    #

    if not evidences:
        return 0.0

    weighted_similarities = [
        e.similarity_score * e.confidence
        for e in evidences
        if e.similarity_score > 0 and e.confidence > 0
    ]

    if not weighted_similarities:
        return 0.0

    avg_weighted_similarity = (
        sum(weighted_similarities) / len(weighted_similarities)
    )

    return min(avg_weighted_similarity, MAX_HISTORICAL_CONFIDENCE)

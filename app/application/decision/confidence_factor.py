# app/application/decision/confidence_factor.py

from typing import Iterable, Mapping

# Tunables (centralizzati)
SIMILARITY_THRESHOLD = 0.75
MAX_HISTORICAL_BONUS = 0.25
PER_DECISION_BONUS = 0.08


def historical_confidence_factor(
    historical_evidence: Iterable[Mapping]
) -> float:
    #
    # Computes a confidence bonus based on historical decision similarity.

    # Rules:
    # - Only decisions with similarity >= SIMILARITY_THRESHOLD count
    # - Missing confidence is treated as neutral (1.0)
    # - Bonus is additive but capped
    # - Returns a value in [0.0, MAX_HISTORICAL_BONUS]
    #

    if not historical_evidence:
        return 0.0

    bonus = 0.0

    for e in historical_evidence:
        similarity = float(e.get("similarity", 0.0))
        confidence = float(e.get("confidence", 1.0) or 1.0)

        if similarity < SIMILARITY_THRESHOLD:
            continue

        bonus += PER_DECISION_BONUS * confidence

    return min(bonus, MAX_HISTORICAL_BONUS)

# app/application/decision/confidence_factor.py

from app.application.decision.historical_evidence import HistoricalDecisionEvidence

SIMILARITY_THRESHOLD = 0.7
CONFIDENCE_BONUS = 0.1
MAX_CONFIDENCE_BONUS = 0.2


def historical_confidence_factor(
    evidences: list[HistoricalDecisionEvidence],
) -> float:
    if not evidences:
        return 0.0

    bonus = 0.0

    for e in evidences:
        similarity = float(e.similarity_score or 0.0)
        confidence = float(e.confidence or 0.0)

        if similarity >= SIMILARITY_THRESHOLD and confidence > 0:
            bonus += CONFIDENCE_BONUS

    return min(bonus, MAX_CONFIDENCE_BONUS)


# app/application/decision/confidence_factor.py

from domain.history.history_repository import HistoricalDecision
from infrastructure.memory.historical_retriever import HistoricalDecisionEvidence



SIMILARITY_THRESHOLD = 0.7
CONFIDENCE_BONUS = 0.1
MAX_CONFIDENCE_BONUS = 0.2

def compute_historical_confidence_factor(
    current_decision: str,
    history: list[HistoricalDecision],
) -> float:
    # FASE 4 – deterministic history

    if not history:
        return 1.0

    matches = [
        h for h in history
        if h.decision == current_decision
    ]

    if not matches:
        return 1.0

    # Simple deterministic reinforcement
    return 1.0 + min(0.1 * len(matches), 0.3)



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


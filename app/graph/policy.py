# app/graph/policy.py

from dataclasses import dataclass
from typing import Literal
from app.graph.state import DecisionState
from domain.history.history_repository import HistoricalDecision
from infrastructure.memory.historical_retriever import HistoricalDecisionEvidence
from domain.metrics.confidence import compute_similarity_confidence_bonus


DecisionOutcome = Literal[
    "retry",
    "continue",
    "fallback",
    "end"
]

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


@dataclass(frozen=True)
class DecisionPolicy:
    min_confidence: float = 0.70
    max_attempts: int = 3

    # ----------------------------------------------
    # Hook per estensioni future (FASE 4)
    # ----------------------------------------------
    def compute_effective_confidence(self, state: DecisionState) -> float | None:
        base = state.get("confidence_base")
        if base is None:
            return None

        historical_factor = state.get("historical_confidence_factor", 1.0)

        return base * historical_factor


    # ----------------------------------------------
    # Policy evaluation
    # ----------------------------------------------
    def evaluate(self, state: DecisionState) -> DecisionOutcome:
        # 1. Decision already finalized
        if state.get("decision_finalized"):
            return "end"

        # 2. Explicit retry requested
        if state.get("needs_retry"):
            if state["attempts"] < self.max_attempts:
                return "retry"
            return "fallback"

        # 3. Confidence-based retry
        confidence = self.compute_effective_confidence(state)
        if confidence is not None and confidence < self.min_confidence:
            if state["attempts"] < self.max_attempts:
                return "retry"
            return "fallback"

        # 4. Analysis available
        if state.get("analysis"):
            return "continue"

        # 5. Safe default
        return "continue"

# app/graph/policy.py

from dataclasses import dataclass
from typing import Literal
from app.graph.state import DecisionState

DecisionOutcome = Literal[
    "retry",
    "continue",
    "fallback",
    "end"
]


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

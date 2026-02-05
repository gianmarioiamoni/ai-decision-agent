# app/graph/policy.py

from dataclasses import dataclass
from typing import Literal

from app.graph.state import DecisionState


DecisionOutcome = Literal[
    "retry",
    "continue",
    "fallback",
    "end",
]

SIMILARITY_THRESHOLD = 0.75

@dataclass(frozen=True)
class DecisionPolicy:
    # ----------------------------------------------
    # Policy thresholds
    # ----------------------------------------------
    min_confidence: float = 0.70
    max_attempts: int = 3

    # ----------------------------------------------
    # Confidence evaluation
    # ----------------------------------------------
    def compute_effective_confidence(self, state: DecisionState) -> float | None:
        base_confidence = state.get("confidence_base")
        if base_confidence is None:
            return None

        historical_factor = state.get("historical_confidence_factor", 1.0)

        return base_confidence * historical_factor

    # ----------------------------------------------
    # Policy evaluation
    # ----------------------------------------------
    def evaluate(self, state: DecisionState) -> DecisionOutcome:
        # 1. Decision already finalized
        if state.get("decision_finalized"):
            return "end"

        # 2. Explicit retry requested
        if state.get("needs_retry"):
            if state.get("attempts", 0) < self.max_attempts:
                return "retry"
            return "fallback"

        # 3. Confidence-based retry
        effective_confidence = self.compute_effective_confidence(state)
        if effective_confidence is not None and effective_confidence < self.min_confidence:
            if state.get("attempts", 0) < self.max_attempts:
                return "retry"
            return "fallback"

        # 4. Analysis available → proceed
        if state.get("analysis"):
            return "continue"

        # 5. Safe default
        return "continue"


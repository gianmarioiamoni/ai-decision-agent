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


@dataclass(frozen=True)
class DecisionPolicy:
    min_confidence: float = 0.70
    max_attempts: int = 3

    # ----------------------------------------------
    # Confidence evaluation (FINAL, NOT BASE)
    # ----------------------------------------------
    def compute_effective_confidence(self, state: DecisionState) -> float | None:
        # We reason ONLY on final confidence
        confidence_final = state.get("confidence_final")
        if confidence_final is None:
            return None

        return confidence_final

    # ----------------------------------------------
    # Policy evaluation (PURE)
    # ----------------------------------------------
    def evaluate(self, state: DecisionState) -> DecisionOutcome:
        # 0. Hard override
        if state.get("force_fallback"):
            return "fallback"

        if state.get("decision_finalized"):
            return "continue"

        # 1. Confidence-based routing (PRIORITY)
        effective_confidence = self.compute_effective_confidence(state)
        if (
            effective_confidence is not None
            and effective_confidence < self.min_confidence
        ):
            return (
                "retry"
                if state.get("attempts", 0) < self.max_attempts
                else "fallback"
            )

        # 1.5 Low confidence → retry
        if state.get("low_confidence"):
            return (
                "retry" 
                if state.get("attempts", 0) < self.max_attempts 
                else "fallback"
            )

        # 2. No context at all → fallback
        if not state.get("authoritative_context", []) and not state.get("similar_decisions", []):
            return "fallback"

        # 3. Default forward
        return "continue"

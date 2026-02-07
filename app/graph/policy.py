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
        # 0. Hard override for tests / emergency
        if state.get("force_fallback"):
            return "fallback"

        # 1. Already finalized → stop
        if state.get("decision_finalized"):
            return "end"

        # 2. Confidence-based routing 
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

        # 4. Default forward
        return "continue"



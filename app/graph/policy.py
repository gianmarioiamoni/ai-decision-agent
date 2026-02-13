# app/graph/policy.py

from dataclasses import dataclass
from typing import Literal
from app.graph.state import DecisionState
from app.constants import MAX_ATTEMPTS

DecisionOutcome = Literal[
    "retry",
    "continue",
    "fallback",
    "end",
]


@dataclass(frozen=True)
class DecisionPolicy:
    min_confidence: float = 0.70
    max_attempts: int = MAX_ATTEMPTS

    # ----------------------------------------------
    # Confidence evaluation (FINAL, NOT BASE)
    # ----------------------------------------------
    def compute_effective_confidence(self, state: DecisionState) -> float | None:
        confidence_final = state.get("confidence_final")
        if confidence_final is None:
            return None
        return confidence_final

    # ----------------------------------------------
    # Policy evaluation (PURE, TOTAL)
    # ----------------------------------------------
    def evaluate(self, state: DecisionState) -> DecisionOutcome:
        # 0. Hard override (tests / emergency)
        if state.get("force_fallback"):
            return "fallback"

        # 1. Finalized decisions MUST continue to finalization
        #    (summarize → persist_history)
        if state.get("decision_finalized"):
            return "continue"

        # 2. Confidence-based retry (priority rule)
        effective_confidence = state.get("confidence_base")
        if (
            effective_confidence is not None
            and effective_confidence < self.min_confidence
        ):
            return (
                "retry"
                if state.get("attempts", 0) < self.max_attempts
                else "fallback"
            )

        # 3. Low-confidence signal (derived metric)
        if state.get("low_confidence"):
            return (
                "retry"
                if state.get("attempts", 0) < self.max_attempts
                else "fallback"
            )

        # 4. No context at all → fallback
        if not state.get("authoritative_context", []) and not state.get("similar_decisions", []):
            return "fallback"

        # 5. DEFAULT SAFE PATH (MANDATORY)
        #    Guarantees totality of the policy
        return "continue"


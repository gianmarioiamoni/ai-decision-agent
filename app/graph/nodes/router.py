# app/graph/router.py

from typing import Literal
from app.graph.state import DecisionState

Route = Literal[
    "retry",
    "continue",
    "fallback",
    "end"
]

MIN_CONFIDENCE = 0.70
MAX_ATTEMPTS = 3


def decision_router(state: DecisionState) -> Route:
    # 1. Decision already finalized
    if state.get("decision_finalized"):
        return "end"

    # 2. Explicit retry requested by analysis
    if state.get("needs_retry"):
        if state["attempts"] < MAX_ATTEMPTS:
            return "retry"
        return "fallback"

    # 3. Low base confidence
    confidence = state.get("confidence_base")
    if confidence is not None and confidence < MIN_CONFIDENCE:
        if state["attempts"] < MAX_ATTEMPTS:
            return "retry"
        return "fallback"

    # 4. Analysis completed → proceed
    if state.get("analysis"):
        return "continue"

    # 5. Safe default
    return "continue"



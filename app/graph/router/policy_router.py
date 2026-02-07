# app/graph/router/policy_router.py

from app.graph.state import DecisionState
from app.graph.policy import DecisionPolicy, DecisionOutcome


def policy_router(state: DecisionState) -> DecisionOutcome:
    state.setdefault("retry_count", 0)
    state.setdefault("needs_retry", False)
    state.setdefault("used_fallback", False)

    # ------------------------------------
    # TERMINATION HAS PRIORITY
    # ------------------------------------
    if state.get("decision_finalized"):
        if state.get("used_fallback"):
            return "fallback"
        return "continue"

    # ------------------------------------
    # RETRY PATH
    # ------------------------------------
    state["retry_count"] += 1
    state["needs_retry"] = True
    return "retry"

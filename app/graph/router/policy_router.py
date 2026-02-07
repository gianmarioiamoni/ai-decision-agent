# app/graph/router/policy_router.py

from app.graph.state import DecisionState
from app.graph.policy import DecisionPolicy, DecisionOutcome


def policy_router(state: DecisionState) -> DecisionOutcome:
    # -------------------------------------------------
    # SAFE INITIALIZATION (router-owned fields)
    # -------------------------------------------------
    state.setdefault("retry_count", 0)
    state.setdefault("attempts", 0)
    state.setdefault("needs_retry", False)
    state.setdefault("used_fallback", False)

    policy = DecisionPolicy()
    outcome = policy.evaluate(state)

    # -------------------------------------------------
    # ROUTING SIDE EFFECTS (router is owner)
    # -------------------------------------------------
    if outcome == "retry":
        state["retry_count"] += 1
        state["attempts"] += 1
        state["needs_retry"] = True

    else:
        state["needs_retry"] = False

    if outcome == "fallback":
        state["used_fallback"] = True
        # ❗ decision_finalized NON qui
        # lo farà fallback_node

    return outcome





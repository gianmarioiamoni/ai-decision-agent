# app/graph/router/policy_router.py

from app.graph.state import DecisionState
from app.graph.policy import DecisionPolicy, DecisionOutcome


def policy_router(state: DecisionState) -> DecisionOutcome:
    policy = DecisionPolicy()

    # -------------------------------------------------
    # ROUTER = OWNER of control semantics
    # -------------------------------------------------
    state.setdefault("decision_finalized", False)
    state.setdefault("used_fallback", False)
    state.setdefault("retry_count", 0)
    state.setdefault("attempts", 0)

    outcome = policy.evaluate(state)
    assert outcome in {"retry", "continue", "fallback", "end"}

    # -------------------------------------------------
    # Semantic side-effects
    # -------------------------------------------------
    if outcome == "retry":
        state["retry_count"] += 1
        state["attempts"] += 1

    elif outcome == "fallback":
        state["used_fallback"] = True
        state["decision_finalized"] = True

    elif outcome == "end":
        state["decision_finalized"] = True

    # IMPORTANT:
    # "continue" MUST always mean:
    # summarize → persist_history
    return outcome



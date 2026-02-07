# app/graph/router/policy_router.py

from app.graph.state import DecisionState
from app.graph.policy import DecisionPolicy, DecisionOutcome

from infrastructure.logging.node_logger import log_node


@log_node("policy_router")
def policy_router(state: DecisionState) -> DecisionOutcome:
    policy = DecisionPolicy()
    outcome = policy.evaluate(state)

    # ------------------------------------
    # ROUTING SIDE EFFECTS (router-owned)
    # ------------------------------------
    if outcome == "retry":
        state["retry_count"] += 1
        state["attempts"] += 1
        state["needs_retry"] = True

    else:
        state["needs_retry"] = False

    if outcome == "fallback":
        state["used_fallback"] = True

    return outcome


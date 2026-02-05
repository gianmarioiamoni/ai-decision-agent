# app/graph/nodes/fallback_node.py

from app.graph.state import DecisionState

from infrastructure.logging.node_logger import log_node


@log_node("fallback")
def fallback_node(state: DecisionState) -> DecisionState:
    # Fallback node invoked when the system cannot reach
    # a confident decision within allowed attempts.
    # This node does NOT perform reasoning.
    # It only finalizes the decision state safely.
    #

    state["decision"] = (
        state.get("decision")
        or "Unable to reach a confident decision with the available information."
    )

    state["justification"] = (
        state.get("justification")
        or "The system attempted multiple analysis and retrieval cycles "
           "but confidence remained below the acceptable threshold."
    )

    state["confidence_final"] = (
        state.get("confidence_final")
        if state.get("confidence_final") is not None
        else 0.4
    )

    state["decision_finalized"] = True

    state.setdefault("errors", []).append(
        "Fallback triggered due to low confidence or repeated ambiguity."
    )

    return state

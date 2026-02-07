# app/graph/nodes/update_confidence_metrics_node.py

from app.graph.state import DecisionState
from infrastructure.logging.node_logger import log_node
from domain.metrics.confidence_drift import compute_confidence_drift


@log_node("update_confidence_metrics")
def update_confidence_metrics_node(state: DecisionState) -> DecisionState:
    confidence = state.get("confidence_final")

    if confidence is None:
        return state

    history = state.get("confidence_final_history", [])
    drift = compute_confidence_drift(history, confidence)

    state["confidence_final_history"] = history + [confidence]
    state["confidence_drift"] = drift

    # --------------------------------------------------
    # CONVERGENCE GUARANTEE (DOMAIN OWNED)
    # --------------------------------------------------
    state.setdefault("attempts", 0)
    state.setdefault("decision_finalized", False)

    state["attempts"] += 1

    MAX_ATTEMPTS = 2

    if state["attempts"] >= MAX_ATTEMPTS:
        state["decision_finalized"] = True

    return state

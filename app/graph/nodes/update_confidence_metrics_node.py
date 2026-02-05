# app/graph/nodes/update_confidence_metrics.py

from infrastructure.logging.node_logger import log_node
from domain.metrics.confidence_drift import compute_confidence_drift

@log_node("update_confidence_metrics")
def update_confidence_metrics(state):
    confidence = state.get("confidence_final")

    if confidence is None:
        return state

    history = state.get("confidence_history", [])
    drift = compute_confidence_drift(history, confidence)

    return {
        **state,
        "confidence_history": history + [confidence],
        "confidence_drift": drift,
    }

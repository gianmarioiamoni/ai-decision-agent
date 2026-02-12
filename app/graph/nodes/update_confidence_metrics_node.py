# app/graph/nodes/update_confidence_metrics_node.py

from app.graph.state import DecisionState
from infrastructure.logging.node_logger import log_node
from domain.metrics.confidence_drift import compute_confidence_drift


@log_node("update_confidence_metrics")
def update_confidence_metrics_node(state: DecisionState) -> DecisionState:
    confidence = state.get("confidence_final")
    raw_similar = state.get("similar_decisions") or []

    weighted_confidence_boost = 1.0

    if raw_similar:
        avg_similarity = sum(d.get("similarity", 0.0) for d in raw_similar if d.get("similarity", 0.0)) / len(raw_similar)
        weighted_confidence_boost = 1 + (avg_similarity * 0.2) 

    if confidence is None:
        return state

    confidence = confidence * weighted_confidence_boost

    # signal for policy, not direct retry
    state["low_confidence"] = confidence < 0.7

    history = state.get("confidence_final_history", [])
    drift = compute_confidence_drift(history, confidence)

    state["confidence_final_history"] = history + [confidence]
    state["confidence_drift"] = drift


    return state

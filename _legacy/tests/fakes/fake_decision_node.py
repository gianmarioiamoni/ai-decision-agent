# tests/fakes/fake_decision_node.py

from app.graph.state import DecisionState


def fake_decision_node(state: DecisionState) -> DecisionState:
    # IMPORTANT: mutate state, do NOT replace it
    state["decision"] = state.get("decision") or "APPROVE"
    state["justification"] = "fake-justification"
    state["confidence_final"] = state.get("confidence_base")
    state["decision_finalized"] = True
    return state

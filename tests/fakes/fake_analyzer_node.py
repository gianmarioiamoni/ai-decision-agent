# tests/fakes/fake_analyzer_node.py

from app.graph.state import DecisionState


def fake_analyzer_node(state: DecisionState) -> DecisionState:
    # IMPORTANT: mutate state, do NOT replace it
    state["analysis"] = "fake-analysis"
    state["confidence_base"] = state.get("confidence_base", 0.7)
    state["needs_retry"] = False
    return state


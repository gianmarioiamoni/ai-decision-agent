# tests/fakes/fake_planner_node.py

from app.graph.state import DecisionState


def fake_planner_node(state: DecisionState) -> DecisionState:
    # IMPORTANT: mutate state, do NOT replace it
    state["plan"] = "fake-plan"
    return state


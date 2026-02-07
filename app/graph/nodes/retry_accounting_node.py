# app/graph/nodes/retry_accounting_node.py

from app.graph.state import DecisionState

def retry_accounting_node(state: DecisionState) -> DecisionState:
    state.setdefault("retry_count", 0)
    state.setdefault("attempts", 0)

    state["retry_count"] += 1
    state["attempts"] += 1

    return state

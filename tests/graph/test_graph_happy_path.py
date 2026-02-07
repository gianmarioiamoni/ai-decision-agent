# tests/graph/test_graph_happy_path.py

def test_graph_happy_path(graph, base_state):
    final_state = graph.invoke(base_state)

    assert final_state.get("plan") is not None
    assert final_state.get("decision") is not None
    assert isinstance(final_state.get("confidence_final"), float)
    assert final_state["confidence_final"] >= 0.0

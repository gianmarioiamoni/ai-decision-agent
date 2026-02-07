# tests/graph/test_graph_fallback.py

def test_graph_fallback_triggered(graph, base_state):
    base_state["force_fallback"] = True
    base_state["confidence_final"] = 0.4
    base_state["confidence_base"] = 0.4

    final_state = graph.invoke(base_state)

    assert final_state.get("used_fallback") is True
    assert final_state.get("decision") is not None

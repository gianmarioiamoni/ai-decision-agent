# tests/graph/test_graph_retry.py

def test_graph_retries_until_confidence_improves(graph, base_state):
    base_state["confidence_final"] = 0.5
    base_state["confidence_base"] = 0.5
    base_state["retry_count"] = 0
    base_state["attempts"] = 0

    final_state = graph.invoke(base_state)

    assert final_state["retry_count"] >= 1
    assert final_state["confidence_final"] >= base_state["confidence_final"]

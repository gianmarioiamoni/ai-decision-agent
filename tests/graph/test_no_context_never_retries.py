# tests/graph/test_no_context_never_retries.py

def test_no_context_never_retries(graph, base_state):
    base_state["confidence_final"] = 0.4
    base_state["authoritative_context"] = []
    base_state["similar_decisions"] = []

    final_state = graph.invoke(base_state)

    assert final_state["retry_count"] == 0
    assert final_state["used_fallback"] is True

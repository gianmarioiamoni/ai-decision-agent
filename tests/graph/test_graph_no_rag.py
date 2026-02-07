# tests/graph/test_graph_no_rag.py

def test_graph_runs_without_rag(graph, base_state):
    final_state = graph.invoke(base_state)

    assert "rag_context" in final_state
    assert isinstance(final_state["rag_context"], str)

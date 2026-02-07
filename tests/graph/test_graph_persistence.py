# tests/graph/test_graph_persistence.py

def test_history_persisted_once(graph, base_state):
    # Stato MINIMO semanticamente valido per la persistenza
    base_state["authoritative_context"] = ["Positive ROI"]
    base_state["similar_decisions"] = []

    base_state["decision"] = "Proceed with AI investment"
    base_state["justification"] = "Expected ROI exceeds threshold"
    base_state["confidence_final"] = 0.85
    base_state["context_hash"] = "test_context_hash_001"

    # 🔑 BLOCCO decision_node effects
    base_state["decision_finalized"] = True

    final_state = graph.invoke(base_state)

    assert final_state["history_persisted"] is True





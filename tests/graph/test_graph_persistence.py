def test_history_persisted_once(graph, base_state):
    # 🔑 CONTEXT IS REQUIRED
    base_state["authoritative_context"] = [
        "Historical data suggests positive ROI"
    ]
    base_state["similar_decisions"] = []

    base_state["decision"] = "Proceed with AI investment"
    base_state["justification"] = "Expected ROI exceeds threshold"
    base_state["confidence_base"] = 0.75
    base_state["confidence_final"] = 0.85
    base_state["context_hash"] = "test_context_hash_001"

    final_state = graph.invoke(base_state)

    assert final_state["history_persisted"] is True




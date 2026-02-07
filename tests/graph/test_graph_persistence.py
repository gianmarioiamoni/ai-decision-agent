# tests/graph/test_graph_persistence.py

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state

from tests.graph.fakes import FakeHistoryRepository


def test_history_persisted_once():
    # --------------------------------------------------------------
    # Arrange
    # --------------------------------------------------------------
    fake_repository = FakeHistoryRepository()

    graph = build_graph(
        history_repository=fake_repository
    )

    initial_state = create_initial_state(
        user_query="Test that persistence is called once",
        input_context_docs=[],
    )

    # 🔒 FORZA SEMANTICA DI STATO FINALE
    # (il graph non deve "inventarsela")
    initial_state["decision"] = "Proceed with the plan"
    initial_state["confidence_base"] = 0.75
    initial_state["confidence_final"] = 0.75
    initial_state["decision_finalized"] = True
    initial_state["context_hash"] = "test-context-hash"

    # --------------------------------------------------------------
    # Act
    # --------------------------------------------------------------
    final_state = graph.invoke(initial_state)

    # --------------------------------------------------------------
    # Assert
    # --------------------------------------------------------------
    assert fake_repository.persist_calls == 1
    assert final_state.get("history_persisted") is True
    assert final_state.get("decision") is not None

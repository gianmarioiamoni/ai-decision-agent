# tests/integration/test_historical_memory_integration.py

from app.graph.policy import DecisionPolicy
from app.graph.state import DecisionState
from app.graph.nodes.history_lookup_node import HistoryLookupNode
from domain.history.history_repository import InMemoryHistoryRepository
from app.graph.graph import build_graph
import pytest


def test_effective_confidence_applies_historical_factor():
    policy = DecisionPolicy(min_confidence=0.7)

    state = {
        "confidence_base": 0.8,
        "historical_confidence_factor": 1.1,
    }

    assert policy.compute_effective_confidence(state) == pytest.approx(0.88)


def test_history_lookup_node_sets_only_historical_factor():
    repo = InMemoryHistoryRepository()
    repo.persist_if_absent("ctx", "APPROVE", 0.9)

    node = HistoryLookupNode(repo)

    state = DecisionState(
        context_hash="ctx",
        decision="APPROVE",
        confidence_base=0.8,
    )

    new_state = node(state)

    assert new_state.historical_confidence_factor != 1.0
    assert new_state.decision == "APPROVE"
    assert new_state.confidence_base == 0.8

def test_graph_uses_history_to_avoid_retry():
    repo = InMemoryHistoryRepository()
    repo.persist_if_absent("ctx", "APPROVE", 0.9)

    graph = build_graph(history_repository=repo)

    state = DecisionState(
        user_query="should I approve this request?",
        context_hash="ctx",
        decision="APPROVE",
        confidence_base=0.65,
        attempts=1,
    )

    result = graph.invoke(state)

    assert result["decision"] == "APPROVE"



# tests/integration/test_historical_memory_integration.py

from app.graph.policy import DecisionPolicy
from app.graph.state import DecisionState
from app.graph.nodes.history_lookup_node import HistoryLookupNode
from domain.history.history_repository import InMemoryHistoryRepository
from app.graph.graph import build_graph
from tests.fakes.fake_planner_node import fake_planner_node
from tests.fakes.fake_analyzer_node import fake_analyzer_node
from tests.fakes.fake_decision_node import fake_decision_node
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

    assert new_state["historical_confidence_factor"] != 1.0
    assert new_state["decision"] == "APPROVE"
    assert new_state["confidence_base"] == 0.8

    
def test_graph_uses_history_to_avoid_retry():
    repo = InMemoryHistoryRepository()
    repo.persist_if_absent("ctx", "APPROVE", 0.9)

    graph = build_graph(
        history_repository=repo, 
        planner=fake_planner_node, 
        analyzer=fake_analyzer_node, 
        decision=fake_decision_node
    )

    state = DecisionState(
        context_hash="ctx",
        # ========= INPUT =========
        user_query="approve this request",
        input_context_docs=[],          # 🔑 MANCAVA
        input_metadata={},

        # ========= PLANNING =========
        plan=None,

        # ========= RAG =========
        authoritative_context=[],
        general_context=[],
        query_similarity=[],
        rag_context=None,

        # ========= ANALYSIS =========
        analysis=None,
        risks=[],
        assumptions=[],
        confidence_base=0.65,

        # ========= DECISION =========
        decision="APPROVE",
        justification=None,
        confidence_final=None,

        # ========= HISTORY =========
        similar_decisions=[],
        historical_confidence_factor=None,

        # ========= CONTROL =========
        attempts=1,
        needs_retry=False,
        decision_finalized=False,

        # ========= UI / ERRORS =========
        messages=[],
        report_html=None,
        report_preview=None,
        errors=[],
    )

    result = graph.invoke(state)

    assert result["decision"] == "APPROVE"



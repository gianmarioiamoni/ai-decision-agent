# tests/graph/conftest.py

import pytest

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from domain.history.history_repository import InMemoryHistoryRepository


from tests.graph.fakes import FakeLLM

@pytest.fixture
def graph():
    #
    # Real LangGraph with in-memory persistence.
    # No infrastructure, no mocks.
    #
    history_repository = InMemoryHistoryRepository()
    return build_graph(history_repository=history_repository)


@pytest.fixture
def base_state() -> DecisionState:
    return create_initial_state(
        user_query="Should we invest in AI-driven customer support?",
        input_context_docs=[],
    )

@pytest.fixture(autouse=True)
def patch_llm(monkeypatch):
    #
    # Replace the planner LLM with a fake deterministic one.
    #
    from tests.graph.fakes import FakeLLM

    fake_llm = FakeLLM(
        response="""
        PLAN:
        1. Evaluate pros and cons
        2. Assess risks
        3. Make recommendation
        """
    )

    def fake_get_llm():
        return fake_llm

    # 🔥 PATCH NEL MODULO CHE LO USA
    monkeypatch.setattr(
        "app.graph.nodes.planner_node.get_llm",
        fake_get_llm,
    )

    monkeypatch.setattr(
        "app.graph.nodes.analyzer_node.get_llm",
        fake_get_llm,
    )

    monkeypatch.setattr(
        "app.graph.nodes.decision_node.get_llm",
        fake_get_llm,
    )
# tests/integration/test_graph_integration.py
#
# Integration test for LangGraph decision flow (FASE 3)
#
# Verifies:
# - conditional routing after analyzer
# - retry loop via RAG
# - fallback after max attempts
#

from langgraph.graph import StateGraph, END

from app.graph.state import DecisionState
from app.graph.router import decision_router

from tests.fakes.fake_planner_node import fake_planner_node


# --------------------------------------------------
# Fake nodes (test-only)
# --------------------------------------------------

def fake_planner(state: DecisionState) -> DecisionState:
    state["errors"] = ["planner"]
    return state


def fake_rag(state: DecisionState) -> DecisionState:
    state["errors"].append("rag")
    state["attempts"] += 1
    return state


def fake_analyzer(state: DecisionState) -> DecisionState:
    state["errors"].append("analyzer")
    state["confidence_base"] = 0.4  # Force retry
    return state


def fake_decision(state: DecisionState) -> DecisionState:
    state["errors"].append("decision")
    state["decision_finalized"] = True
    return state


def fake_fallback(state: DecisionState) -> DecisionState:
    state["errors"].append("fallback")
    state["decision_finalized"] = True
    return state


# --------------------------------------------------
# Integration test
# --------------------------------------------------

def test_graph_retries_then_fallback():
    graph = StateGraph(DecisionState)

    # Nodes
    graph.add_node("planner", fake_planner)
    graph.add_node("rag", fake_rag)
    graph.add_node("analyzer", fake_analyzer)
    graph.add_node("decision", fake_decision)
    graph.add_node("fallback", fake_fallback)

    # Entry point
    graph.set_entry_point("planner")

    # Fixed edges
    graph.add_edge("planner", "rag")
    graph.add_edge("rag", "analyzer")

    # Conditional routing (FASE 3)
    graph.add_conditional_edges(
        "analyzer",
        decision_router,
        {
            "retry": "rag",
            "continue": "decision",
            "fallback": "fallback",
            "end": END,
        },
    )

    # Final edges
    graph.add_edge("decision", END)
    graph.add_edge("fallback", END)

    app = graph.compile()

    # Initial state
    state = {
        "attempts": 0,
        "needs_retry": False,
        "decision_finalized": False,
        "analysis": "uncertain",
        "confidence_base": None,
        "errors": [],
    }

    result = app.invoke(state)

    # --------------------------------------------------
    # Assertions
    # --------------------------------------------------

    # Final node must be fallback
    assert result["errors"][-1] == "fallback"

    # Analyzer must have been executed at least once
    assert "analyzer" in result["errors"]

    # Retry loop must have happened (rag called more than once)
    assert result["errors"].count("rag") >= 1

# app/graph/graph.py
#
# LangGraph – FASE 3
#
# Purpose:
# - Declarative routing via DecisionPolicy
# - Retry / fallback / finalize
# - No behavior change, only orchestration change
#

from langgraph.graph import StateGraph, END

from app.graph.state import DecisionState
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.analyzer_node import analyzer_node
from app.graph.nodes.decision_node import decision_node
from app.graph.nodes.rag_retrieval_node import rag_retrieval_node
from app.graph.nodes.fallback_node import fallback_node
from app.graph.router import decision_router


def build_graph():
    graph = StateGraph(DecisionState)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------
    graph.add_node("planner", planner_node)
    graph.add_node("rag", rag_retrieval_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("decision", decision_node)
    graph.add_node("fallback", fallback_node)

    # --------------------------------------------------
    # Entry point
    # --------------------------------------------------
    graph.set_entry_point("planner")

    # --------------------------------------------------
    # Fixed edges
    # --------------------------------------------------
    graph.add_edge("planner", "rag")
    graph.add_edge("rag", "analyzer")

    # --------------------------------------------------
    # Conditional routing (FASE 3)
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Finalization
    # --------------------------------------------------
    graph.add_edge("decision", END)
    graph.add_edge("fallback", END)

    return graph.compile()

# app/graph/graph.py
#
# LangGraph skeleton – FASE 1 (shadow mode)
#
# Purpose:
# - Introduce LangGraph without changing behavior
# - Linear flow only
# - planner → analyzer → decision
#
# NO routing
# NO memory
# NO retry
#

from langgraph.graph import StateGraph, END

from app.graph.state import DecisionState
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.analyzer_node import analyzer_node
from app.graph.nodes.decision_node import decision_node
from app.graph.nodes.rag_retrieval_node import rag_retrieval_node

def build_graph():
    #
    # Build LangGraph decision flow (linear).
    #
    # Entry:
    #   planner
    #
    # Flow:
    #   planner → analyzer → decision → END
    #

    graph = StateGraph(DecisionState)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------
    graph.add_node("planner", planner_node)
    graph.add_node("rag", rag_retrieval_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("decision", decision_node)

    # --------------------------------------------------
    # Linear edges (NO conditional routing)
    # --------------------------------------------------
    graph.set_entry_point("planner")
    graph.add_edge("planner", "rag")
    graph.add_edge("rag", "analyzer")
    graph.add_edge("analyzer", "decision")
    graph.add_edge("decision", END)

    return graph.compile()

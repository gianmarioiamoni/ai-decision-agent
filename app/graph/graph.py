# app/graph/graph.py
#
# LangGraph – FASE 4
#
# Purpose:
# - Declarative routing via DecisionPolicy (FASE 3)
# - History as first-class citizen (FASE 4)
# - No behavior change
#

from langgraph.graph import StateGraph, END

from app.graph.state import DecisionState

from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.analyzer_node import analyzer_node
from app.graph.nodes.decision_node import decision_node
from app.graph.nodes.rag_retrieval_node import rag_retrieval_node
from app.graph.nodes.fallback_node import fallback_node

from app.graph.nodes.history_lookup_node import HistoryLookupNode
from app.graph.nodes.persist_history_node import PersistHistoryNode

from app.graph.router import decision_router

from infrastructure.memory.chroma_client import get_chroma_collection
from domain.history.history_repository import ChromaHistoryRepository


def build_graph():
    # ==================================================
    # Composition root – Infrastructure
    # ==================================================

    collection = get_chroma_collection()

    history_repository = ChromaHistoryRepository(
        collection=collection
    )

    # ==================================================
    # Graph
    # ==================================================

    graph = StateGraph(DecisionState)

    # --------------------------------------------------
    # Nodes
    # --------------------------------------------------
    graph.add_node("planner", planner_node)
    graph.add_node("rag", rag_retrieval_node)
    graph.add_node("analyzer", analyzer_node)

    # 🔑 FASE 4 – History nodes
    graph.add_node(
        "history_lookup",
        HistoryLookupNode(history_repository)
    )

    graph.add_node("decision", decision_node)

    graph.add_node(
        "persist_history",
        PersistHistoryNode(history_repository)
    )

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

    # 🔑 FASE 4 – History before routing
    graph.add_edge("analyzer", "history_lookup")

    # --------------------------------------------------
    # Conditional routing (FASE 3)
    # --------------------------------------------------
    graph.add_conditional_edges(
        "history_lookup",
        decision_router,
        {
            "retry": "rag",
            "continue": "decision",
            "fallback": "fallback",
            "end": END,
        },
    )

    # --------------------------------------------------
    # Finalization (FASE 4)
    # --------------------------------------------------
    graph.add_edge("decision", "persist_history")
    graph.add_edge("persist_history", END)

    graph.add_edge("fallback", END)

    return graph.compile()



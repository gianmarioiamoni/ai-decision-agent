# app/graph/graph.py

from langgraph.graph import StateGraph, END

from app.graph.state import DecisionState

from app.graph.nodes.intake import intake_node
from app.graph.nodes.rag_retrieval_node import rag_retrieval_node
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.decision_node import decision_node
from app.graph.nodes.update_confidence_metrics_node import update_confidence_metrics_node
from app.graph.nodes.summarize_node import summarize_node
from app.graph.nodes.persist_history_node import PersistHistoryNode
from app.graph.nodes.analyzer_node import analyzer_node
from app.graph.nodes.fallback_node import fallback_node
from app.graph.nodes.retry_accounting_node import retry_accounting_node
from app.graph.nodes.history_lookup_node import HistoryLookupNode
from app.graph.nodes.historical_influence_node import HistoricalInfluenceNode


from app.graph.router.policy_router import policy_router

from domain.history.history_repository import (
    HistoryRepository,
    ChromaHistoryRepository,
)
from infrastructure.memory.chroma_client import get_chroma_collection


def build_graph(history_repository: HistoryRepository | None = None):
    # --------------------------------------------------------------
    # Infrastructure wiring
    # --------------------------------------------------------------
    if history_repository is None:
        chroma_memory = get_chroma_collection()
        history_repository = ChromaHistoryRepository(chroma_memory)

    persist_history_node = PersistHistoryNode(history_repository)
    history_lookup_node = HistoryLookupNode(history_repository)
    historical_influence_node = HistoricalInfluenceNode()


    graph = StateGraph(DecisionState)

    # --- Nodes ---
    graph.add_node("intake", intake_node)
    graph.add_node("rag_retrieval", rag_retrieval_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("planner", planner_node)
    graph.add_node("decision", decision_node)
    graph.add_node("update_confidence_metrics", update_confidence_metrics_node)
    graph.add_node("retry_accounting", retry_accounting_node)
    graph.add_node("fallback", fallback_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("persist_history", persist_history_node)
    graph.add_node("history_lookup", history_lookup_node)
    graph.add_node("historical_influence", historical_influence_node)


    # --- Edges ---
    graph.set_entry_point("intake")

    graph.add_edge("intake", "history_lookup")
    graph.add_edge("history_lookup", "historical_influence")
    graph.add_edge("historical_influence", "rag_retrieval")
    graph.add_edge("rag_retrieval", "analyzer")
    graph.add_edge("analyzer", "planner")
    graph.add_edge("planner", "decision")
    graph.add_edge("decision", "update_confidence_metrics")

    # --- Router (CRITICAL FIX HERE) ---
    graph.add_conditional_edges(
        "update_confidence_metrics",
        policy_router,
        {
            "retry": "retry_accounting",
            "continue": "summarize",
            "fallback": "fallback",
            "end": "summarize",   # 🔑 FIX
        },
    )

    graph.add_edge("retry_accounting", "planner")
    graph.add_edge("fallback", "summarize")
    graph.add_edge("summarize", "persist_history")
    graph.add_edge("persist_history", END)

    return graph.compile()

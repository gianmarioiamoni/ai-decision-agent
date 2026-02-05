# graph/build_graph.py

from langgraph.graph import StateGraph, END

from app.graph.state import DecisionState

from app.graph.nodes.intake import intake_node
from app.graph.nodes.rag_retrieval_node import rag_retrieval_node
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.decision_node import decision_node
from app.graph.nodes.update_confidence_metrics_node import update_confidence_metrics_node
from app.graph.nodes.summarize_node import summarize_node
from app.graph.nodes.persist_history_node import PersistHistoryNode

from app.graph.router.policy_router import policy_router


from domain.history.history_repository import HistoryRepository
from infrastructure.memory.historical_writer import HistoricalWriter
from infrastructure.memory.chroma_client import get_chroma_memory

def build_graph():
    # --------------------------------------------------------------
    # Infrastructure wiring (graph-local)
    # --------------------------------------------------------------
    chroma_memory = get_chroma_memory()
    historical_writer = HistoricalWriter(chroma_memory)
    history_repository = HistoryRepository(
        writer=historical_writer,
    )

    persist_history_node = PersistHistoryNode(
        history_repository=history_repository,
    )

    graph = StateGraph(DecisionState)

    # --- Nodes ---
    graph.add_node("intake", intake_node)
    graph.add_node("rag_retrieval", rag_retrieval_node)
    graph.add_node("planner", planner_node)
    graph.add_node("decision", decision_node)
    graph.add_node(
        "update_confidence_metrics",
        update_confidence_metrics_node,
    )
    graph.add_node("summarize", summarize_node)
    graph.add_node("persist_history", persist_history_node)

    # --- Edges (lineari) ---
    graph.set_entry_point("intake")

    graph.add_edge("intake", "rag_retrieval")
    graph.add_edge("rag_retrieval", "planner")
    graph.add_edge("planner", "decision")
    graph.add_edge("decision", "update_confidence_metrics")

    # --- Router ---
    graph.add_conditional_edges(
        "update_confidence_metrics",
        policy_router,
        {
            "retry": "planner",
            "continue": "summarize",
            "fallback": "summarize",
            "end": END,
        },
    )

    graph.add_edge("summarize", "persist_history")
    graph.add_edge("persist_history", END)

    return graph.compile()

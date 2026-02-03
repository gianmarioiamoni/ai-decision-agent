# app/graph/nodes/historical_retriever.py

from typing import Optional

from app.graph.state import DecisionState
from infrastructure.memory.historical_retriever import HistoricalDecisionRetriever


_retriever_instance: Optional[HistoricalDecisionRetriever] = None


def _get_historical_retriever() -> HistoricalDecisionRetriever:
    global _retriever_instance

    if _retriever_instance is None:
        # ⬇️ IMPORT LAZY (OK IN FASE 0)
        from infrastructure.memory.chroma_client import get_chroma_collection

        collection = get_chroma_collection()
        _retriever_instance = HistoricalDecisionRetriever(collection)

    return _retriever_instance


def historical_retriever_node(state: DecisionState) -> DecisionState:
    if not state.user_query:
        raise ValueError("Historical retriever requires a valid user query")

    retriever = _get_historical_retriever()

    similar_decisions = retriever.retrieve(
        query=state.user_query,
        k=3,
    )

    print(
        f"[HISTORICAL_RETRIEVER] 🧠 Retrieved {len(similar_decisions)} historical decisions"
    )

    state.similar_decisions = similar_decisions
    return state

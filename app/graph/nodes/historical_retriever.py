# app/graph/nodes/historical_retriever.py

from typing import Dict

from app.graph.state import DecisionState
from infrastructure.memory.historical_retriever import (
    HistoricalDecisionRetriever,
)
from infrastructure.memory.chroma_client import get_chroma_collection


_collection = get_chroma_collection()
_historical_retriever = HistoricalDecisionRetriever(_collection)


def historical_retriever_node(state: DecisionState) -> Dict:
    question = state.get("question")

    if not question:
        raise ValueError("Historical retriever requires a valid question")

    evidences = _historical_retriever.retrieve(
        query=question,
        k=3,
    )

    print(
        f"[HISTORICAL_RETRIEVER] 🧠 Retrieved {len(evidences)} historical decisions"
    )

    return {
        "historical_evidence": evidences,
    }

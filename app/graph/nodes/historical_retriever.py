# app/graph/nodes/historical_retriever.py

from typing import Dict, Mapping, Any, Optional

from infrastructure.memory.historical_retriever import HistoricalDecisionRetriever


_retriever_instance: Optional[HistoricalDecisionRetriever] = None


def _get_historical_retriever() -> HistoricalDecisionRetriever:
    global _retriever_instance

    if _retriever_instance is None:
        # ⬇️ IMPORT LAZY (CRITICO)
        from infrastructure.memory.chroma_client import get_chroma_collection

        collection = get_chroma_collection()
        _retriever_instance = HistoricalDecisionRetriever(collection)

    return _retriever_instance


def historical_retriever_node(state: Mapping[str, Any]) -> Dict:
    question = state.get("question")

    if not question:
        raise ValueError("Historical retriever requires a valid question")

    retriever = _get_historical_retriever()

    evidences = retriever.retrieve(
        query=question,
        k=3,
    )

    print(
        f"[HISTORICAL_RETRIEVER] 🧠 Retrieved {len(evidences)} historical decisions"
    )

    return {
        "historical_evidence": evidences,
    }


# app/graph/nodes/history_lookup_node.py

from app.graph.state import DecisionState
from app.constants import HISTORICAL_TOP_K
from domain.history.history_repository import HistoryRepository
from infrastructure.logging.node_logger import log_node



class HistoryLookupNode:
    #
    # Retrieves semantically similar historical decisions.
    # Owner of `similar_decisions`.
    #

    def __init__(self, history_repository: HistoryRepository):
        self._history_repository = history_repository

    @log_node("history_lookup")
    def __call__(self, state: DecisionState) -> DecisionState:

        query_text = state.get("user_query")

        if not query_text:
            state["similar_decisions"] = []
            return state

        history = self._history_repository.lookup_similar(
            query_text=query_text,
            top_k=HISTORICAL_TOP_K,
        )

        state["similar_decisions"] = [
            {
                "context_hash": item.context_hash,
                "decision": item.decision,
                "confidence": float(item.confidence),
                "similarity": float(item.similarity or 0.0),
                "timestamp": item.timestamp
            }
            for item in history
        ]

        print("SIMILAR DECISIONS:", state["similar_decisions"])

        return state


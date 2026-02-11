# app/graph/nodes/history_lookup_node.py

from app.graph.state import DecisionState
from domain.history.history_repository import HistoryRepository
from infrastructure.logging.node_logger import log_node


class HistoryLookupNode:
    #
    # Retrieves similar historical decisions based on context hash.
    # Owner of `similar_decisions`.
    #

    def __init__(self, history_repository: HistoryRepository):
        self._history_repository = history_repository

    @log_node("history_lookup")
    def __call__(self, state: DecisionState) -> DecisionState:
        context_hash = state.get("context_hash")

        if not context_hash:
            state["similar_decisions"] = []
            return state

        history = self._history_repository.lookup(context_hash)

        state["similar_decisions"] = [
            {
                "context_hash": item.context_hash,
                "decision": item.decision,
                "confidence": item.confidence,
                "similarity": 1.0,  # exact hash match
            }
            for item in history
        ]

        print("SIMILAR DECISIONS:", state["similar_decisions"])

        return state

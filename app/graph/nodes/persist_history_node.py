# persist_history_node.py
from domain.history.history_repository import HistoryRepository
from app.graph.state import DecisionState

from infrastructure.logging.node_logger import log_node

@log_node("persist_history")
class PersistHistoryNode:
    def __init__(self, history_repository: HistoryRepository):
        self._history_repository = history_repository

    def __call__(self, state: DecisionState) -> DecisionState:
        self._history_repository.persist_if_absent(
            context_hash=state["context_hash"],
            decision=state["decision"],
            confidence=state["confidence_final"]
        )
        return state


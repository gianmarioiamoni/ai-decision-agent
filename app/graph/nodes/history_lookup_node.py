# app/graph/nodes/history_lookup_node.py
from app.graph.state import DecisionState
from domain.history.history_repository import HistoryRepository
from app.application.decision.confidence_factor import compute_historical_confidence_factor


class HistoryLookupNode:
    def __init__(self, history_repository: HistoryRepository):
        self._history_repository = history_repository

    def __call__(self, state: DecisionState) -> DecisionState:
        history = self._history_repository.lookup(state.context_hash)

        factor = compute_historical_confidence_factor(
            current_decision=state.decision,
            history=history
        )

        state.historical_confidence_factor = factor
        return state


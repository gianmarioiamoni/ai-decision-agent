# app/graph/nodes/persist_history_node.py

from domain.history.history_repository import HistoryRepository
from app.graph.state import DecisionState
from infrastructure.logging.node_logger import log_node


@log_node("persist_history")
class PersistHistoryNode:
    #
    # Persists the final decision snapshot exactly once.
    # Idempotent and domain-driven: persistence depends only
    # on semantic completeness, not on control flags.
    #
    def __init__(self, history_repository: HistoryRepository):
        self._history_repository = history_repository

    def __call__(self, state: DecisionState) -> DecisionState:
        # --------------------------------------------------
        # Guard: persist exactly once
        # --------------------------------------------------
        if state.get("history_persisted", False):
            return state

        # --------------------------------------------------
        # Required domain fields (semantic contract)
        # --------------------------------------------------
        context_hash = state.get("context_hash")
        decision = state.get("decision")
        confidence = state.get("confidence_final")

        if context_hash is None or decision is None or confidence is None:
            # Upstream state not semantically complete → do nothing
            return state

        # --------------------------------------------------
        # Persist (idempotent by repository contract)
        # --------------------------------------------------
        self._history_repository.persist_if_absent(
            context_hash=context_hash,
            decision=decision,
            confidence=confidence,
        )

        state["history_persisted"] = True
        return state




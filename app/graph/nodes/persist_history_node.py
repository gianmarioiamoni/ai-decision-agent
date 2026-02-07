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
        # -------------------------------------------
        # Graph-phase guard: only after summarize
        # -------------------------------------------
        if state.get("justification") is None:
            return state

        # -------------------------------------------
        # Idempetency guard 
        # -------------------------------------------
        if state.get("history_persisted"):
            return state

        context_hash = state.get("context_hash")
        decision = state.get("decision")
        confidence = state.get("confidence_final")

        if context_hash is None or decision is None or confidence is None:
            return state

        self._history_repository.persist_if_absent(
            context_hash=context_hash,
            decision=decision,
            confidence=confidence,
        )

        # -------------------------------------------
        # Graph-level semantic: execution finalized
        # -------------------------------------------
        state["history_persisted"] = True

        return state

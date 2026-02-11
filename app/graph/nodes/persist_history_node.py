# app/graph/nodes/persist_history_node.py

from domain.history.history_repository import HistoryRepository
from app.graph.state import DecisionState


class PersistHistoryNode:
    #
    # Persists the final decision snapshot exactly once.
    # Idempotent and domain-driven.
    # Semantic owner of `history_persisted`.
    #
    def __init__(self, history_repository: HistoryRepository):
        self._history_repository = history_repository

    def __call__(self, state: DecisionState) -> DecisionState:
        # -------------------------------------------
        # Semantic ownership
        # -------------------------------------------
        state.setdefault("history_persisted", False)

        # Idempotency guard
        if state["history_persisted"]:
            return state

        context_hash = state.get("context_hash")
        decision = state.get("decision")
        confidence = state.get("confidence_final")

        # -------------------------------------------
        # Domain guard: persistence may be skipped
        # -------------------------------------------
        if context_hash is not None and decision is not None and confidence is not None:
            self._history_repository.persist_if_absent(
                context_hash=context_hash,
                decision=decision,
                confidence=confidence,
            )

        # -------------------------------------------
        # ✅ ALWAYS mark semantic completion
        # -------------------------------------------
        state["history_persisted"] = True

        print("PERSISTING:", context_hash, decision[:60], confidence)


        return state


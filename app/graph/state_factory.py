# app/graph/state_factory.py

from app.graph.state import DecisionState


def create_initial_state(
    user_query: str,
    input_context_docs: list | None = None,
) -> DecisionState:

    if input_context_docs is None:
        input_context_docs = []

    return {
        # --------------------------------------------------
        # Core input
        # --------------------------------------------------
        "user_query": user_query,
        "input_context_docs": input_context_docs,

        # --------------------------------------------------
        # LLM / reasoning
        # --------------------------------------------------
        "analysis": None,
        "messages": [],

        # --------------------------------------------------
        # Decision
        # --------------------------------------------------
        "decision": None,
        "decision_finalized": False,

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------
        "confidence_base": None,
        "confidence_final": None,
        "confidence_final_history": [],

        # --------------------------------------------------
        # Control & routing (CRITICAL)
        # --------------------------------------------------
        "retry_count": 0,
        "attempts": 0,
        "needs_retry": False,
        "used_fallback": False,

        # --------------------------------------------------
        # Persistence
        # --------------------------------------------------
        "context_hash": hash(user_query),
        "history_persisted": False,

        # --------------------------------------------------
        # Optional enrichment
        # --------------------------------------------------
        "rag_context": "",
        "similar_decisions": [],
        "authoritative_context": [],
        "assumptions": [],
    }

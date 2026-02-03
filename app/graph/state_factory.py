# app/graph/state_factory.py

from app.graph.state import DecisionState


def create_initial_state(
    *,
    user_query: str,
    input_context_docs: list,
    input_metadata: dict | None = None,
) -> DecisionState:
    return {
        # CONVERSATION
        "messages": [],

        # INPUT
        "user_query": user_query,
        "input_context_docs": input_context_docs,
        "input_metadata": input_metadata or {},

        # PLANNING
        "plan": None,

        # RAG
        "authoritative_context": [],
        "general_context": [],
        "query_similarity": [],
        "rag_context": None,

        # ANALYSIS
        "analysis": None,
        "risks": [],
        "assumptions": [],
        "confidence_base": None,

        # DECISION
        "decision": None,
        "justification": None,
        "confidence_final": None,

        # HISTORICAL
        "similar_decisions": [],
        "historical_confidence_factor": None,

        # CONTROL / ROUTING
        "attempts": 0,
        "needs_retry": False,
        "decision_finalized": False,

        # REPORTING / UI
        "report_html": None,
        "report_preview": None,

        # ERROR HANDLING
        "errors": [],
    }

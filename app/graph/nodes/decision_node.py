# app/graph/nodes/decision_node.py

from langchain_core.messages import AIMessage
from app.graph.state import DecisionState
from app.prompts.builders import DecisionPromptBuilder
from app.llm.llm_provider import get_llm
from infrastructure.logging.node_logger import log_node
from app.domain.decision.decision_summary import extract_decision_summary

from app.prompts.constants import (
    DEFAULT_CONFIDENCE_NO_HISTORY,
    DEFAULT_CONFIDENCE_WITH_HISTORY,
)

@log_node("decision")
def decision_node(
    state: DecisionState,
    llm=None,
) -> DecisionState:
    # -------------------------------------------------
    # SAFE INITIALIZATION
    # -------------------------------------------------
    state.setdefault("messages", [])

    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------
    if not state.get("analysis"):
        raise ValueError("Decision node requires analysis")

    # -------------------------------------------------
    # INPUT ADAPTATION
    # -------------------------------------------------
    rag_context = state.get("rag_context") or ""
    raw_similar = state.get("similar_decisions") or []

    adapted_similar = [
        {
            "decision_id": d.get("decision_id", f"hist-{i}"),
            "decision": d.get("decision"),
            "similarity": d.get("similarity") or d.get("similarity_score") or 1.0,
            "content": d.get("decision", ""),
        }
        for i, d in enumerate(raw_similar)
    ]

    has_history = len(adapted_similar) > 0

    # -------------------------------------------------
    # HISTORICAL CONFIDENCE FACTOR (DOMAIN OWNER)
    # -------------------------------------------------
    state["historical_confidence_factor"] = 1.1 if has_history else 1.0

    # -------------------------------------------------
    # PROMPT
    # -------------------------------------------------
    bundle = DecisionPromptBuilder.build(
        question=state["user_query"],
        analysis=state["analysis"],
        rag_context=rag_context,
        similar_decisions=adapted_similar,
    )

    llm = llm or get_llm()
    response = llm.invoke(
        [bundle.system_message, bundle.human_message]
    )

    decision_text = response.content.strip()

    # -------------------------------------------------
    # DOMAIN: DECISION & JUSTIFICATION
    # -------------------------------------------------
    state["decision"] = decision_text
    state["justification"] = decision_text

    # -------------------------------------------------
    # DOMAIN: CONFIDENCE (NUMERIC, SINGLE SOURCE OF TRUTH)
    # -------------------------------------------------
    confidence_base = (
        DEFAULT_CONFIDENCE_WITH_HISTORY
        if has_history
        else DEFAULT_CONFIDENCE_NO_HISTORY
    )

    confidence_final = confidence_base * state["historical_confidence_factor"]

    state["confidence_base"] = confidence_base
    state["confidence_final"] = confidence_final

    # -------------------------------------------------
    # USER-FACING MESSAGE (SUMMARY ONLY)
    # -------------------------------------------------
    summary = extract_decision_summary(decision_text)

    state["messages"].append(
        AIMessage(
            content=(
                f"{summary}\n\n"
                "If you’d like, you can provide additional context, "
                "ask for alternatives, or request a deeper analysis."
            )
        )
    )

    return state

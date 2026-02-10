# app/graph/nodes/decision_node.py

from langchain_core.messages import AIMessage

from app.graph.state import DecisionState
from app.prompts.builders import DecisionPromptBuilder
from app.llm.llm_provider import get_llm
from infrastructure.logging.node_logger import log_node

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
    adapted_similar = []

    for i, d in enumerate(raw_similar):
        adapted_similar.append({
            "decision_id": d.get("decision_id", f"hist-{i}"),
            "decision": d.get("decision"),
            "similarity": d.get("similarity") or d.get("similarity_score") or 1.0,
            "content": d.get("decision", ""),
        })

    has_history = len(adapted_similar) > 0

    # -------------------------------------------------
    # HISTORICAL CONFIDENCE FACTOR (OWNER)
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
    # JUSTIFICATION (DOMAIN, NOT CHAT)
    # -------------------------------------------------
    state["justification"] = decision_text

    # -------------------------------------------------
    # CONFIDENCE (DOMAIN)
    # -------------------------------------------------
    confidence_base = (
        DEFAULT_CONFIDENCE_WITH_HISTORY
        if has_history
        else DEFAULT_CONFIDENCE_NO_HISTORY
    )

    confidence_final = confidence_base * state["historical_confidence_factor"]

    # -------------------------------------------------
    # UPDATE STATE
    # -------------------------------------------------
    state["decision"] = decision_text
    state["confidence_base"] = confidence_base
    state["confidence_final"] = confidence_final

    # -------------------------------------------------
    # USER-FACING CHAT MESSAGE (SINGLE, CLEAN)
    # -------------------------------------------------
    chat_message = (
        f"{decision_text}\n\n"
        "If you’d like, you can provide additional context, "
        "ask for alternatives, or request a deeper analysis."
    )

    state["messages"].append(
        AIMessage(content=chat_message)
    )

    return state


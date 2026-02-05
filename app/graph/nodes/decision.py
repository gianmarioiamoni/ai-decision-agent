# app/graph/nodes/decision.py
# Decision node – LangGraph compliant, confidence-aware
# Responsibilities:
# - Generate final decision
# - Compute final confidence using precomputed factors
# - Emit final messages
#
# NO domain logic
# NO historical computation
# NO routing

import re
from typing import List

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from app.graph.state import DecisionState
from app.prompts.builders import DecisionPromptBuilder


# ------------------------------------------------------------------
# LLM FACTORY
# ------------------------------------------------------------------

def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        temperature=0.1,
        model="gpt-4o-mini",
    )


# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------

def _parse_bullets(text: str) -> List[str]:
    lines = [
        line.strip().lstrip("-• ").strip()
        for line in text.splitlines()
        if line.strip().startswith(("-", "•"))
    ]
    return lines or [text.strip()]


# ------------------------------------------------------------------
# MAIN NODE
# ------------------------------------------------------------------

def decision_node(
    state: DecisionState,
    llm: ChatOpenAI | None = None,
) -> DecisionState:
    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    if not state.get("user_query"):
        raise ValueError("Decision node requires user_query")

    if not state.get("analysis"):
        raise ValueError("Decision node requires analysis")

    # ------------------------------------------------------------------
    # BUILD PROMPT
    # ------------------------------------------------------------------

    similar_decisions = [
        {
            "decision": e.get("decision"),
            "confidence": e.get("confidence"),
            "similarity": e.get("similarity"),
        }
        for e in state.get("similar_decisions", [])
    ]

    bundle = DecisionPromptBuilder.build(
        question=state["user_query"],
        analysis=state["analysis"],
        rag_context="\n\n".join(state.get("authoritative_context", [])),
        similar_decisions=similar_decisions,
    )

    # ------------------------------------------------------------------
    # LLM INVOCATION
    # ------------------------------------------------------------------

    llm = llm or _get_llm()

    response = llm.invoke(
        [
            bundle.system_message,
            bundle.human_message,
        ]
    )

    content = response.content.strip()

    # ------------------------------------------------------------------
    # PARSE RESPONSE
    # ------------------------------------------------------------------

    decision_text = content
    confidence_base: float | None = None

    decision_match = re.search(
        r"Decision[:\s]+(.+?)(?=Confidence:|$)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if decision_match:
        decision_text = decision_match.group(1).strip()

    confidence_match = re.search(
        r"Confidence[:\s]+([\d.]+)",
        content,
        re.IGNORECASE,
    )
    if confidence_match:
        confidence_base = float(confidence_match.group(1))

    # ------------------------------------------------------------------
    # CONFIDENCE COMPUTATION (ORCHESTRATION ONLY)
    # ------------------------------------------------------------------

    historical_factor = state.get("historical_confidence_factor", 1.0)

    if confidence_base is not None:
        confidence_final = min(confidence_base * historical_factor, 1.0)
    else:
        confidence_final = None

    # ------------------------------------------------------------------
    # UPDATE STATE
    # ------------------------------------------------------------------

    state["decision"] = decision_text
    state["confidence_base"] = confidence_base
    state["confidence_final"] = confidence_final

    state["messages"].append(AIMessage(content=decision_text))

    if confidence_final is not None:
        state["messages"].append(
            AIMessage(content=f"Confidence: {confidence_final:.2f}")
        )

    return state

# app/graph/nodes/decision_node.py
# Decision node – LangGraph compliant, confidence-aware
# Responsibilities:
# - Generate final decision
# - Apply deterministic historical confidence bonus
# - Emit final messages
#
# NO routing
# NO retries
# NO persistence
#
# CONTROL / ROUTING
# These fields are signals only.
# Routing decisions are handled exclusively by DecisionPolicy.
#
# NOTE:
# Each field has a single writer node.
# Routing decisions are handled exclusively by DecisionPolicy.
# Nodes may write control flags but must never route on them.
#


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
            "decision": d.get("decision"),
            "confidence": d.get("confidence"),
            "similarity": d.get("similarity"),
        }
        for d in state.get("similar_decisions", [])
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
    # HISTORICAL CONFIDENCE BONUS (DETERMINISTIC)
    # ------------------------------------------------------------------

    historical_bonus = 0.0

    for d in state.get("similar_decisions", []):
        similarity = d.get("similarity_score") or 0.0
        confidence = d.get("confidence") or 0.0

        if similarity >= 0.75 and confidence > 0:
            historical_bonus += 0.05

    historical_bonus = min(historical_bonus, 0.2)

    # ------------------------------------------------------------------
    # FINAL CONFIDENCE
    # ------------------------------------------------------------------

    if confidence_base is not None:
        confidence_final = min(confidence_base + historical_bonus, 1.0)
    else:
        confidence_final = None

    # ------------------------------------------------------------------
    # UPDATE STATE
    # ------------------------------------------------------------------

    state["decision"] = decision_text
    state["confidence_base"] = confidence_base  # belongs to DECISION, not ANALYSIS
    state["historical_confidence_factor"] = historical_bonus
    state["confidence_final"] = confidence_final
    state["confidence_breakdown"] = {
        "base": confidence_base or 0.0,
        "historical": historical_bonus,
        "final": confidence_final or 0.0,
    }

    state["messages"].append(AIMessage(content=decision_text))

    if confidence_final is not None:
        state["messages"].append(
            AIMessage(content=f"Confidence: {confidence_final:.2f}")
        )

    return state


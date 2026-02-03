# app/graph/nodes/decision.py
# Decision node – confidence-aware, history-consumer only
# Generates:
# - final decision + confidence
# - concise short_rationale for historical memory

import re
from typing import List

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from domain.decision.decision_state import DecisionState
from app.prompts.builders import DecisionPromptBuilder
from app.application.decision.confidence_factor import (
    historical_confidence_factor,
)


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

def _build_short_rationale_prompt(
    question: str,
    decision: str,
    analysis: str,
) -> List[AIMessage]:
    #
    # Dedicated prompt for generating a SHORT rationale for memory.
    # This MUST stay small and clean.
    #
    # Args:
    #     question: The user's question
    #     decision: The final decision
    #     analysis: The supporting analysis
    #
    # Returns:
    #     A list of AIMessages containing the system and human messages
    #

    system = AIMessage(
        content=(
            "You are a decision support system.\n"
            "Your task is to extract ONLY the decisive rationale.\n"
            "Be concise and factual."
        )
    )

    human = AIMessage(
        content=(
            f"Question:\n{question}\n\n"
            f"Final Decision:\n{decision}\n\n"
            f"Supporting Analysis:\n{analysis}\n\n"
            "Provide a concise rationale for this decision.\n\n"
            "Requirements:\n"
            "- Maximum 5 bullet points\n"
            "- Each bullet must be a single sentence\n"
            "- Focus ONLY on decisive factors\n"
            "- Do NOT restate the full analysis\n"
            "- Do NOT include the decision text\n"
            "- Do NOT include any headers or explanations\n"
            "- Output ONLY the bullet list"
        )
    )

    return [system, human]


def _parse_bullets(text: str) -> List[str]:
    #
    # Normalize bullet output to a clean list of bullet strings.
    #
    # Args:
    #     text: The text to parse
    #
    # Returns:
    #     A list of bullet strings
    #

    lines = [
        line.strip().lstrip("-• ").strip()
        for line in text.splitlines()
        if line.strip().startswith(("-", "•"))
    ]

    if not lines:
        return [text.strip()]

    return lines


# ------------------------------------------------------------------
# MAIN NODE (STEP 0.3 COMPLIANT)
# ------------------------------------------------------------------

def decision_node(
    state: DecisionState,
    llm: ChatOpenAI | None = None,
) -> DecisionState:
    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    if not state.user_query:
        raise ValueError("Decision node requires a valid user_query")

    if not state.reasoning:
        raise ValueError("Decision node requires analysis reasoning")

    # ------------------------------------------------------------------
    # DEBUG LOGGING
    # ------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("⚖️ DECISION PHASE")
    print("=" * 60)
    print(f"📝 Question: {state.user_query[:100]}...")

    if state.authoritative_context:
        print(f"✅ RAG Context Available ({len(state.authoritative_context)} chunks)")
    else:
        print("❌ No authoritative RAG context")

    print(f"📚 Historical Evidence Items: {len(state.historical_evidence)}")

    # ------------------------------------------------------------------
    # FORMAT HISTORICAL EVIDENCE (FOR PROMPT ONLY)
    # ------------------------------------------------------------------

    similar_decisions = [
        {
            "decision": e.decision,
            "confidence": e.confidence,
            "similarity": getattr(e, "similarity_score", None),
        }
        for e in state.historical_evidence
    ]

    # ------------------------------------------------------------------
    # BUILD DECISION PROMPT
    # ------------------------------------------------------------------

    bundle = DecisionPromptBuilder.build(
        question=state.user_query,
        analysis=state.reasoning,
        rag_context="\n\n".join(state.authoritative_context),
        similar_decisions=similar_decisions,
    )

    print("\n📤 System Prompt (first 400 chars):")
    print(bundle.system_message.content[:400] + "...")
    print("\n📤 Human Prompt (first 400 chars):")
    print(bundle.human_message.content[:400] + "...")
    print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # LLM INVOCATION (DECISION)
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
    # PARSE DECISION RESPONSE
    # ------------------------------------------------------------------

    decision_text = ""
    confidence_value: float | None = None

    decision_match = re.search(
        r"Decision[:\s]+(.+?)(?=Confidence:|$)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if decision_match:
        decision_text = decision_match.group(1).strip()
    else:
        decision_text = content

    confidence_match = re.search(
        r"Confidence[:\s]+([\d.]+)",
        content,
        re.IGNORECASE,
    )
    if confidence_match:
        confidence_value = float(confidence_match.group(1))
    else:
        confidence_value = 0.75

    # ------------------------------------------------------------------
    # CONFIDENCE ADJUSTMENT (HISTORICAL ONLY)
    # ------------------------------------------------------------------

    history_factor = historical_confidence_factor(state.historical_evidence)
    final_confidence = min(confidence_value + history_factor, 1.0)

    print(f"📊 Base Confidence: {confidence_value:.2f}")
    print(f"📊 Historical Factor: {history_factor:.2f}")
    print(f"📊 Final Confidence: {final_confidence:.2f}")

    # ------------------------------------------------------------------
    # SHORT RATIONALE GENERATION (SECOND LLM CALL)
    # ------------------------------------------------------------------

    rationale_prompt = _build_short_rationale_prompt(
        question=state.user_query,
        decision=decision_text,
        analysis=state.reasoning,
    )

    rationale_response = llm.invoke(rationale_prompt)
    short_rationale = _parse_bullets(rationale_response.content.strip())

    # ------------------------------------------------------------------
    # UPDATE STATE (NO DICT RETURN)
    # ------------------------------------------------------------------

    state.decision = decision_text
    state.confidence_base = confidence_value
    state.confidence_final = final_confidence
    state.short_rationale = short_rationale
    state.status = "DECIDED"
    state.messages.append(
        AIMessage(content=decision_text)
    )
    state.messages.append(
        AIMessage(content=f"Confidence: {final_confidence:.2f}")
    )
    state.messages.append(
        AIMessage(content=short_rationale)
    )

    return state


# app/graph/nodes/decision.py
# Decision node – confidence-aware, history-consumer only
# Generates BOTH:
# - final decision + confidence
# - concise short_rationale for historical memory

from typing import Dict, Mapping, Any, List
import re

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

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
    """
    Dedicated prompt for generating a SHORT rationale for memory.
    This MUST stay small and clean.
    """
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


def _parse_bullets(text: str) -> str:
    """
    Normalize bullet output to a clean, newline-separated bullet list.
    """
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith(("-", "•"))
    ]

    if not lines:
        # fallback: single sentence
        return f"- {text.strip()}"

    return "\n".join(lines)


# ------------------------------------------------------------------
# MAIN NODE
# ------------------------------------------------------------------

def decision_node(
    state: Mapping[str, Any],
    llm: ChatOpenAI | None = None,
) -> Dict[str, Any]:

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    question = state.get("question")
    analysis = state.get("analysis")
    rag_context = state.get("rag_context", "")
    historical_evidence = state.get("historical_evidence", [])

    if not question:
        raise ValueError("Decision node requires a valid question in state")
    if not analysis:
        raise ValueError("Decision node requires an analysis to make a decision")

    # ------------------------------------------------------------------
    # DEBUG LOGGING
    # ------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("⚖️ DECISION PHASE")
    print("=" * 60)
    print(f"📝 Question: {question[:100]}...")

    if rag_context:
        print(f"✅ RAG Context Available ({len(rag_context)} chars)")
    else:
        print("❌ No authoritative RAG context")

    print(f"📚 Historical Evidence Items: {len(historical_evidence)}")

    # ------------------------------------------------------------------
    # FORMAT HISTORICAL EVIDENCE (FOR PROMPT ONLY)
    # ------------------------------------------------------------------

    similar_decisions = [
        {
            "decision": e.decision,
            "confidence": e.confidence,
            "similarity": e.similarity_score,
        }
        for e in historical_evidence
    ]

    # ------------------------------------------------------------------
    # BUILD DECISION PROMPT
    # ------------------------------------------------------------------

    bundle = DecisionPromptBuilder.build(
        question=question,
        analysis=analysis,
        rag_context=rag_context,
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
    confidence_value = None
    context_factors = "No specific organizational context influenced this decision."

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
        confidence_value = float(confidence_match.group(1))

    factors_match = re.search(
        r"Contextual Factors Influencing This Decision[:\s]*(.+)",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if factors_match:
        context_factors = factors_match.group(1).strip()

    if not decision_text:
        decision_text = content

    if confidence_value is None:
        confidence_value = 0.75

    # ------------------------------------------------------------------
    # CONFIDENCE ADJUSTMENT (HISTORICAL ONLY)
    # ------------------------------------------------------------------

    history_factor = historical_confidence_factor(historical_evidence)
    final_confidence = min(confidence_value + history_factor, 1.0)

    print(f"📊 Base Confidence: {confidence_value:.2f}")
    print(f"📊 Historical Factor: {history_factor:.2f}")
    print(f"📊 Final Confidence: {final_confidence:.2f}")

    # ------------------------------------------------------------------
    # SHORT RATIONALE GENERATION (SECOND LLM CALL)
    # ------------------------------------------------------------------

    rationale_prompt = _build_short_rationale_prompt(
        question=question,
        decision=decision_text,
        analysis=analysis,
    )

    rationale_response = llm.invoke(rationale_prompt)
    short_rationale = _parse_bullets(rationale_response.content.strip())

    # ------------------------------------------------------------------
    # FINAL CHAT MESSAGE (UI ONLY)
    # ------------------------------------------------------------------

    assistant_message = AIMessage(
        content=(
            f"Decision:\n{decision_text}\n\n"
            f"Confidence: {final_confidence:.2f}\n\n"
            f"Contextual Factors:\n{context_factors}"
        )
    )

    # ------------------------------------------------------------------
    # RETURN STATE UPDATE
    # ------------------------------------------------------------------

    return {
        "decision": decision_text,
        "confidence": final_confidence,
        "short_rationale": short_rationale,  # 🔑 MEMORY-SAFE
        "confidence_factors": {
            "base": confidence_value,
            "historical": history_factor,
        },
        "rag_significant": bundle.rag_significant,
        "rag_mode": bundle.rag_mode,
        "messages": [assistant_message],
    }

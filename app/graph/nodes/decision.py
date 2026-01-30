# app/graph/nodes/decision.py
# Decision node – confidence-aware, history-consumer only

from typing import Dict, Mapping, Any
import re

from langchain_core.messages import AIMessage

from app.prompts.builders import DecisionPromptBuilder
from app.application.decision.confidence_factor import (
    historical_confidence_factor,
)

def _get_llm():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        temperature=0.1,
        model="gpt-4o-mini",
    )

def decision_node(state: Mapping[str, Any], llm=None) -> Dict:
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

    print(
        f"📚 Historical Evidence Items: {len(historical_evidence)}"
    )

    # ------------------------------------------------------------------
    # BUILD DECISION PROMPT (NO HISTORY HERE!)
    # ------------------------------------------------------------------

    bundle = DecisionPromptBuilder.build(
        question=question,
        analysis=analysis,
        rag_context=rag_context,
    )

    print("\n📤 System Prompt (first 400 chars):")
    print(bundle.system_message.content[:400] + "...")
    print("\n📤 Human Prompt (first 400 chars):")
    print(bundle.human_message.content[:400] + "...")
    print("=" * 60 + "\n")

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
    # CONFIDENCE ADJUSTMENT (HISTORICAL FACTOR ONLY)
    # ------------------------------------------------------------------

    history_factor = historical_confidence_factor(historical_evidence)
    final_confidence = min(confidence_value + history_factor, 1.0)

    print(f"📊 Base Confidence: {confidence_value:.2f}")
    print(f"📊 Historical Factor: {history_factor:.2f}")
    print(f"📊 Final Confidence: {final_confidence:.2f}")

    # ------------------------------------------------------------------
    # FINAL CHAT MESSAGE
    # ------------------------------------------------------------------

    assistant_message = AIMessage(
        content=(
            f"Decision:\n{decision_text}\n\n"
            f"Confidence: {final_confidence:.2f}\n\n"
            f"Contextual Factors:\n{context_factors}"
        )
    )

    return {
        "decision": decision_text,
        "confidence": final_confidence,
        "confidence_factors": {
            "base": confidence_value,
            "historical": history_factor,
        },
        "rag_significant": bundle.rag_significant,
        "rag_mode": bundle.rag_mode,
        "messages": [assistant_message],
    }


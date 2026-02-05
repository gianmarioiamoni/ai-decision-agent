# app/graph/nodes/decision_node.py
#
# Decision node – LangGraph compatible (FASE 1)
#
# Responsibilities:
# - Validate analysis
# - Generate final decision + justification
# - Compute final confidence (base + historical factor)
# - Write final outputs into DecisionState
#
# NO routing
# NO retry
# NO memory persistence
#

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

from app.graph.state import DecisionState
from app.application.decision.confidence_factor import (
    historical_confidence_factor,
)
from app.prompts.builders import DecisionPromptBuilder

from infrastructure.logging.node_logger import log_node


@log_node("decision")
def decision_node(state: DecisionState) -> DecisionState:
    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    if not state["analysis"]:
        raise ValueError("Decision node requires analysis")

    # ------------------------------------------------------------------
    # DEBUG LOGGING
    # ------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("⚖️  DECISION PHASE (GRAPH MODE)")
    print("=" * 60)
    print(f"📝 Question: {state['user_query'][:100]}...")
    print("=" * 60)

    if state["authoritative_context"]:
        print(
            f"✅ RAG Context Available ({len(state['authoritative_context'])} chunks)"
        )
    else:
        print("❌ No authoritative RAG context")

    print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # BUILD PROMPT
    # ------------------------------------------------------------------

    bundle = DecisionPromptBuilder.build(
        question=state["user_query"],
        analysis=state["analysis"],
        rag_context=state["rag_context"],
        similar_decisions=state["similar_decisions"],
    )

    # ------------------------------------------------------------------
    # LLM INVOCATION
    # ------------------------------------------------------------------

    llm = ChatOpenAI(
        temperature=0.2,
        model="gpt-4o-mini",
    )

    response = llm.invoke(
        [
            bundle.system_message,
            bundle.human_message,
        ]
    )

    decision_text = response.content.strip()

    # ------------------------------------------------------------------
    # CONFIDENCE COMPUTATION
    # ------------------------------------------------------------------

    confidence_base = state["confidence_base"] or 0.0

    history_factor = historical_confidence_factor(
        state["similar_decisions"]
    )

    final_confidence = min(confidence_base + history_factor, 1.0)

    print(f"📊 Base Confidence: {confidence_base:.2f}")
    print(f"📊 Historical Factor: {history_factor:.2f}")
    print(f"📊 Final Confidence: {final_confidence:.2f}")

    # ------------------------------------------------------------------
    # UPDATE STATE
    # ------------------------------------------------------------------

    state["decision"] = decision_text
    state["justification"] = decision_text  # same text in FASE 1
    state["confidence_final"] = final_confidence

    # Conversation output (FINAL node responsibility)
    state["messages"].append(
        AIMessage(content=decision_text)
    )
    state["messages"].append(
        AIMessage(content=f"Confidence: {final_confidence:.2f}")
    )

    return state

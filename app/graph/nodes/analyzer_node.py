# app/graph/nodes/analyzer_node.py
#
# Analyzer node – LangGraph compatible (FASE 1)
#
# Independent from planner:
# - NO plan dependency
# - Uses authoritative RAG context
# - Uses historical decisions (if present)
#
# Deterministic, non-streaming version for graph execution.
#

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

from app.graph.state import DecisionState
from app.prompts.builders import AnalyzerIndependentPromptBuilder
from app.prompts.historical_context_formatter import format_historical_context


def analyzer_node(state: DecisionState) -> DecisionState:
    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    if not state["user_query"]:
        raise ValueError("Analyzer node requires a valid user_query")

    # ------------------------------------------------------------------
    # INPUT EXTRACTION
    # ------------------------------------------------------------------

    question = state["user_query"]
    rag_context = state["rag_context"] or ""
    retrieved_docs = state["authoritative_context"]
    historical_context = format_historical_context(
        state["similar_decisions"]
    )

    # ------------------------------------------------------------------
    # DEBUG LOGGING
    # ------------------------------------------------------------------

    print("\n" + "=" * 60)
    print("🔍 ANALYZER PHASE (GRAPH MODE)")
    print("=" * 60)
    print(f"📝 Question: {question[:100]}...")

    if rag_context:
        print(f"✅ RAG Context Available ({len(rag_context)} chars)")
    else:
        print("❌ NO RAG Context")

    if historical_context:
        print(f"✅ Historical Context Available ({len(historical_context)} chars)")
    else:
        print("❌ NO Historical Context")

    print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # BUILD PROMPT (NO PLAN DEPENDENCY)
    # ------------------------------------------------------------------

    bundle = AnalyzerIndependentPromptBuilder.build(
        question=question,
        rag_context=rag_context,
        retrieved_docs=retrieved_docs,
        historical_context=historical_context,
    )

    # ------------------------------------------------------------------
    # LLM INVOCATION (NON-STREAMING)
    # ------------------------------------------------------------------

    llm = ChatOpenAI(
        temperature=0.3,
        model="gpt-4o-mini",
        streaming=False,
    )

    parser = StrOutputParser()

    analysis_text = parser.invoke(
        llm.invoke(
            [
                bundle.system_message,
                bundle.human_message,
            ]
        )
    ).strip()

    # ------------------------------------------------------------------
    # UPDATE STATE
    # ------------------------------------------------------------------

    state["analysis"] = analysis_text

    # NOTE:
    # confidence_base is computed downstream (decision node)
    # or left None if analyzer does not compute it

    return state

# app/graph/nodes/analyzer_node.py
#
# Analyzer node.
#
# Responsibilities:
# - Validate input
# - Build prompt using AnalyzerIndependentPromptBuilder
# - Invoke LLM
#
# NOTE:
# - Analyzer operates independently of the planner.
# - Analyzer does not depend on the plan.

from app.graph.state import DecisionState
from app.prompts.builders import AnalyzerIndependentPromptBuilder
from app.graph.utils.historical_context_formatter import format_historical_context
from app.llm.llm_provider import get_llm

from infrastructure.logging.node_logger import log_node


@log_node("analyzer")
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

    print("✅ RAG Context Available" if rag_context else "❌ NO RAG Context")
    print("✅ Historical Context Available" if historical_context else "❌ NO Historical Context")
    print("=" * 60 + "\n")

    # ------------------------------------------------------------------
    # BUILD PROMPT
    # ------------------------------------------------------------------
    bundle = AnalyzerIndependentPromptBuilder.build(
        question=question,
        rag_context=rag_context,
        retrieved_docs=retrieved_docs,
        historical_context=historical_context,
    )

    # ------------------------------------------------------------------
    # LLM INVOCATION (STREAMING)
    # ------------------------------------------------------------------
    llm = get_llm()

    buffer: list[str] = []

    for chunk in llm.stream(
        [
            bundle.system_message,
            bundle.human_message,
        ]
    ):
        token = chunk.content or ""
        buffer.append(token)

        # 🔴 STREAMING FIELD (progressive)
        state["analysis_stream"] = "".join(buffer)

    # ------------------------------------------------------------------
    # FINAL COMMIT (DETERMINISTIC)
    # ------------------------------------------------------------------
    final_text = state.get("analysis_stream", "").strip()
    state["analysis"] = final_text

    return state


# app/ui/handlers/graph_handler_parallel.py
#
# Parallel graph execution handler using RunnableParallel.
# FIX 3: Deterministic RAG enable/disable based on vectorstore state.

import time

# Import streaming nodes
from app.graph.nodes.intake import intake_node
from app.graph.nodes.planner_streaming import planner_node_stream
from app.graph.nodes.retriever import retriever_node
from app.graph.nodes.rag_node import rag_node
from app.graph.nodes.analyzer_independent_streaming import analyzer_independent_stream
from app.graph.nodes.decision import decision_node
from app.graph.nodes.summarize import summarize_node

from app.rag.file_manager import get_file_manager
from app.rag.vectorstore_manager import get_vectorstore_manager

# Import modular components
from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.handlers.loaders.context_logger import ContextLogger
from app.rag.context_loader import ContextLoader

# Import markdown conversion for streaming display
from app.ui.utils.markdown_utils import md_to_plain_text


def run_graph_parallel_streaming(
    question,
    rag_files=None,
):
    #
    # Run the decision graph with PARALLEL execution.
    #
    try:
        # --------------------------------------------------------------
        # INIT
        # --------------------------------------------------------------
        loader = ContextLoader()
        logger = ContextLogger()
        assembler = OutputAssembler()

        file_manager = get_file_manager()
        vectorstore_manager = get_vectorstore_manager()

        # 🔑 FIX 3: RAG DECISION (SINGLE SOURCE OF TRUTH)
        rag_enabled = vectorstore_manager.count() > 0

        print(
            f"[RAG DECISION] {'✅ RAG ENABLED' if rag_enabled else '❌ RAG DISABLED'} "
            f"(embeddings={vectorstore_manager.count()})"
        )

        # Load context documents (non-RAG context)
        context_docs = loader.load()
        storage_info = file_manager.get_storage_info()

        logger.log_loading_summary(context_docs, storage_info)

        # --------------------------------------------------------------
        # PHASE 1: INTAKE
        # --------------------------------------------------------------
        state = {
            "messages": [],
            "question": question,
            "plan": None,
            "retrieved_docs": [],
            "analysis": None,
            "decision": None,
            "confidence": None,
            "attempts": 0,
            "report_html": None,
            "report_preview": None,
            "context_docs": context_docs,
            "rag_context": None,
            "decision_finalized": False,
        }

        intake_result = intake_node(state)
        state.update(intake_result)

        # --------------------------------------------------------------
        # PHASE 2: RAG (CONDITIONAL – FIX 3)
        # --------------------------------------------------------------
        if rag_enabled:
            print("[RAG] 🔍 Executing RAG node")
            rag_result = rag_node(state)
            state.update(rag_result)
            state["messages"].extend(rag_result.get("messages", []))
        else:
            print("[RAG] ⏭️ Skipped (no embeddings present)")
            state["rag_context"] = None

        # --------------------------------------------------------------
        # PHASE 3: RETRIEVER (historical / non-user RAG)
        # --------------------------------------------------------------
        retriever_result = retriever_node(state)
        state.update(retriever_result)
        state["messages"].extend(retriever_result.get("messages", []))

        # --------------------------------------------------------------
        # PHASE 4: PARALLEL STREAMING (Planner + Analyzer)
        # --------------------------------------------------------------
        print("\n" + "=" * 60)
        print("🚀 PARALLEL STREAMING EXECUTION: Planner + Analyzer")
        print("=" * 60 + "\n")

        planner_gen = planner_node_stream(question, context_docs)
        analyzer_gen = analyzer_independent_stream(
            question,
            state["rag_context"],
            state["retrieved_docs"],
        )

        plan_accumulated = ""
        analysis_accumulated = ""
        planner_done = False
        analyzer_done = False

        while not (planner_done and analyzer_done):
            if not planner_done:
                try:
                    plan_accumulated = next(planner_gen)
                except StopIteration:
                    planner_done = True

            if not analyzer_done:
                try:
                    analysis_accumulated = next(analyzer_gen)
                except StopIteration:
                    analyzer_done = True

            plan_display = md_to_plain_text(plan_accumulated) if plan_accumulated else ""
            analysis_display = (
                md_to_plain_text(analysis_accumulated)
                if analysis_accumulated
                else ""
            )

            if not planner_done and plan_display:
                plan_display = "⏳ Generating plan in parallel...\n\n" + plan_display
            if not analyzer_done and analysis_display:
                analysis_display = (
                    "⏳ Analyzing independently...\n\n" + analysis_display
                )

            yield _format_streaming_output(
                plan=plan_display,
                analysis=analysis_display,
                decision="",
                confidence=0.0,
                messages="",
                report_preview="",
                report_file_path=None,
                historical_html="",
                rag_evidence_html="",
            )

            time.sleep(0.05)

        print("\n" + "=" * 60)
        print("✅ PARALLEL STREAMING COMPLETE")
        print("=" * 60 + "\n")

        # --------------------------------------------------------------
        # FINAL PHASES (Decision + Summarize)
        # --------------------------------------------------------------
        state["plan"] = plan_accumulated
        state["analysis"] = analysis_accumulated

        decision_result = decision_node(state)
        decision_messages = decision_result.pop("messages", [])
        state.update(decision_result)
        state["messages"].extend(decision_messages)

        summarize_result = summarize_node(state)
        state.update(summarize_result)

        (
            plan,
            analysis,
            decision,
            confidence,
            messages,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(state, context_docs)

        yield _format_streaming_output(
            plan=plan,
            analysis=analysis,
            decision=decision,
            confidence=confidence,
            messages=messages,
            report_preview=report_preview,
            report_file_path=report_file_path,
            historical_html=historical_html,
            rag_evidence_html=rag_evidence_html,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        yield _format_error_output(str(e))


# ==============================================================================
# Helper Functions
# ==============================================================================

def _format_streaming_output(
    plan,
    analysis,
    decision,
    confidence,
    messages,
    report_preview,
    report_file_path,
    historical_html,
    rag_evidence_html,
):
    return (
        plan,
        analysis,
        decision,
        confidence,
        messages,
        report_preview,
        report_file_path,
        historical_html,
        rag_evidence_html,
    )


def _format_error_output(error_message):
    error_msg = f"❌ Error: {error_message}"
    error_html = f"<p style='color: red;'>{error_msg}</p>"
    return (
        error_msg,
        error_msg,
        error_msg,
        0.0,
        error_html,
        error_html,
        None,
        error_html,
        error_html,
    )

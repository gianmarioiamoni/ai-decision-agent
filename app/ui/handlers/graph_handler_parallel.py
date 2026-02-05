# app/ui/handlers/graph_handler_parallel.py
#
# Graph execution handler (DecisionState-based).
# Deterministic, testable, UI-boundary safe.
#

from langchain_core.messages import AIMessage

from app.graph.nodes.intake import intake_node
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.retriever import retriever_node
from app.graph.nodes.rag_node import rag_node
from app.graph.nodes.decision import decision_node
from app.graph.nodes.summarize import summarize_node

from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.rag.file_manager import get_file_manager
from app.rag.vectorstore_manager import get_vectorstore_manager
from app.rag.context_loader import ContextLoader

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.handlers.loaders.context_logger import ContextLogger
from app.ui.components.output_messages import messages_to_chatbot

from infrastructure.memory.historical_writer import HistoricalDecisionWriter
from infrastructure.memory.chroma_client import get_chroma_collection
from infrastructure.memory.historical_retriever import HistoricalDecisionRetriever


# ==============================================================================
# Infrastructure (initialized once)
# ==============================================================================

_chroma_collection = get_chroma_collection()
historical_writer = HistoricalDecisionWriter(_chroma_collection)
historical_retriever = HistoricalDecisionRetriever(_chroma_collection)


# ==============================================================================
# Helper formatters
# ==============================================================================

def _format_error_output(error_message: str):
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


# ==============================================================================
# UI mapping (explicit boundary)
# ==============================================================================

def _map_state_to_ui_outputs(
    state: DecisionState,
    chat_history,
    report_preview: str | None,
    report_file_path: str | None,
    historical_html: str | None,
    rag_evidence_html: str | None,
):
    #
    # Explicit UI contract.
    # UI must never access DecisionState directly.
    #
    return (
        state.get("plan"),
        state.get("analysis"),
        state.get("decision"),
        state.get("confidence_final"),
        chat_history,
        report_preview,
        report_file_path,
        historical_html,
        rag_evidence_html,
    )


# ==============================================================================
# Main entrypoint
# ==============================================================================

def run_graph_parallel_streaming(
    question: str,
    rag_files=None,
):
    #
    # Executes the decision workflow using DecisionState.
    # Streaming is temporarily disabled for stability.
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

        rag_enabled = vectorstore_manager.count() > 0

        print(
            f"[RAG DECISION] {'✅ RAG ENABLED' if rag_enabled else '❌ RAG DISABLED'} "
            f"(embeddings={vectorstore_manager.count()})"
        )

        context_docs = loader.load()
        storage_info = file_manager.get_storage_info()
        logger.log_loading_summary(context_docs, storage_info)

        # --------------------------------------------------------------
        # PHASE 1: INTAKE
        # --------------------------------------------------------------
        state = create_initial_state(
            user_query=question,
            input_context_docs=context_docs,
        )

        state = intake_node(state)

        # --------------------------------------------------------------
        # PHASE 2: RAG (optional)
        # --------------------------------------------------------------
        # if rag_enabled:
        #     state = rag_node(state)

        # --------------------------------------------------------------
        # PHASE 3a: TECHNICAL RETRIEVER
        # --------------------------------------------------------------
        state = retriever_node(state)

        # --------------------------------------------------------------
        # PHASE 3b: HISTORICAL CONTEXT (OUTSIDE GRAPH)
        # --------------------------------------------------------------
        historical_evidence = historical_retriever.retrieve(
            query=state["user_query"],
            limit=5,
        )

        state["similar_decisions"] = historical_evidence
        state["history_used"] = bool(historical_evidence)

        # --------------------------------------------------------------
        # PHASE 4: PLANNING
        # --------------------------------------------------------------
        state = planner_node(state)

        # --------------------------------------------------------------
        # PHASE 5: ANALYSIS (temporary fallback)
        # --------------------------------------------------------------
        if not state.get("analysis"):
            state["analysis"] = (
                "No dedicated analytical step was executed. "
                "Decision is based on plan, retrieved knowledge "
                "and historical evidence when available."
            )

        # --------------------------------------------------------------
        # PHASE 6: DECISION
        # --------------------------------------------------------------
        state = decision_node(state)

        # --------------------------------------------------------------
        # PHASE 7: SUMMARIZE / REPORT
        # --------------------------------------------------------------
        state = summarize_node(state)

        # --------------------------------------------------------------
        # PHASE 8: PERSIST HISTORY
        # --------------------------------------------------------------
        historical_writer.persist_from_state(state)

        # Ensure rag_context is always a string for UI
        if isinstance(state.get("rag_context"), list):
            state["rag_context"] = "\n\n".join(state["rag_context"])

        # --------------------------------------------------------------
        # UI FORMATTING (no state access beyond this point)
        # --------------------------------------------------------------
        (
            plan,
            analysis,
            decision,
            confidence,
            messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(state, context_docs)

        try:
            chat_history = messages_to_chatbot(state.get("messages", []))
        except Exception as e:
            print(f"⚠️ Error converting messages: {e}")
            chat_history = []

        # --------------------------------------------------------------
        # UI BOUNDARY
        # --------------------------------------------------------------
        return _map_state_to_ui_outputs(
            state=state,
            chat_history=chat_history,
            report_preview=report_preview,
            report_file_path=report_file_path,
            historical_html=historical_html,
            rag_evidence_html=rag_evidence_html,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return _format_error_output(str(e))

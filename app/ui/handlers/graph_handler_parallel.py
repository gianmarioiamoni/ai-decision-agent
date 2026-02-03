# app/ui/handlers/graph_handler_parallel.py
#
# Graph execution handler (DecisionState-based).
# STEP 0.4.x FIX:
# - Remove dict-based state handling
# - Remove update() and [] access
# - Operate ONLY on DecisionState
# - Disable streaming temporarily for stability

from langchain_core.messages import AIMessage

from app.graph.nodes.intake import intake_node
from app.graph.nodes.planner_node import planner_node
from app.graph.nodes.retriever import retriever_node
from app.graph.nodes.rag_node import rag_node
from app.graph.nodes.decision import decision_node
from app.graph.nodes.summarize import summarize_node
from app.graph.nodes.historical_retriever import historical_retriever_node

from app.rag.file_manager import get_file_manager
from app.rag.vectorstore_manager import get_vectorstore_manager
from app.rag.context_loader import ContextLoader

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.handlers.loaders.context_logger import ContextLogger
from app.ui.components.output_messages import messages_to_chatbot

from app.application.decision.history_reader import load_decision_history
from app.application.decision.decision_state_mapper import map_state_to_decision_record

from infrastructure.memory.historical_writer import HistoricalDecisionWriter
from infrastructure.memory.chroma_client import get_chroma_collection

from app.graph.state import DecisionState


# ==============================================================================
# Infrastructure (initialized once)
# ==============================================================================

_chroma_collection = get_chroma_collection()
historical_writer = HistoricalDecisionWriter(_chroma_collection)


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
        state = DecisionState(
            user_query=question,
            input_context_docs=context_docs,
        )

        state = intake_node(state)

        # --------------------------------------------------------------
        # PHASE 2: RAG (optional)
        # --------------------------------------------------------------
        if rag_enabled:
            state = rag_node(state)

        # --------------------------------------------------------------
        # PHASE 3a: TECHNICAL RETRIEVER
        # --------------------------------------------------------------
        state = retriever_node(state)

        # --------------------------------------------------------------
        # PHASE 3b: HISTORICAL RETRIEVER
        # --------------------------------------------------------------
        state = historical_retriever_node(state)

        # --------------------------------------------------------------
        # PHASE 4: PLANNING
        # --------------------------------------------------------------
        state = planner_node(state)

        # --------------------------------------------------------------
        # PHASE 5: ANALYSIS (TEMPORARY FALLBACK – PHASE 0)
        # --------------------------------------------------------------
        if not state["analysis"]  :
            state["analysis"] = (
                "No dedicated analytical analysis step was executed. "
                "The decision is based on the proposed plan, retrieved knowledge, "
                "and historical evidence when available." # TODO: remove this fallback
            )

        if not state["analysis"]:
            state["analysis"] = state["analysis"] or ""

        # --------------------------------------------------------------
        # PHASE 6: DECISION
        # --------------------------------------------------------------
        state = decision_node(state)

        # --------------------------------------------------------------
        # SHADOW MODE: LANGGRAPH (FASE 1)
        # --------------------------------------------------------------
        from app.graph.graph import build_graph
        try:
            graph = build_graph()

            # IMPORTANT:
            # We invoke LangGraph on a COPY of the state
            graph_state = graph.invoke(state.copy()) # type: ignore

            print("\n" + "=" * 60)
            print("🧪 LANGGRAPH SHADOW EXECUTION")
            print("=" * 60)
            print(f"Legacy decision:   {state['decision']}")
            print(f"LangGraph decision:{graph_state['decision']}")
            print("=" * 60 + "\n")
        except Exception as e:
            print("❌ LangGraph shadow execution failed")
            print(e)


        # --------------------------------------------------------------
        # PHASE 7: SUMMARIZE / REPORT
        # --------------------------------------------------------------
        state = summarize_node(state)

        # --------------------------------------------------------------
        # PHASE 8: PERSIST HISTORY
        # --------------------------------------------------------------
        record = map_state_to_decision_record(state)
        historical_writer.persist(record)

        # Load full historical evidence for UI
        full_history = load_decision_history(limit=20)
        state["similar_decisions"] = full_history

        # --------------------------------------------------------------
        # UI ASSEMBLY
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

        chat_history = messages_to_chatbot(state["messages"])

        return (
            plan,
            analysis,
            decision,
            confidence,
            chat_history,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return _format_error_output(str(e))


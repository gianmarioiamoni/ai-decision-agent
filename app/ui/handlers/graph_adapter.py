# app/ui/handlers/graph_handler_parallel.py
#
# Graph execution handler (DecisionState-based).
# Deterministic, testable, UI-boundary safe.
#

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.components.output_messages import messages_to_chatbot

GRAPH = build_graph()

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
# Main entrypoint (UI → Graph → UI)
# ==============================================================================

def run_graph(
    question: str,
    rag_files=None,
):
    #
    # Executes the decision workflow via LangGraph.
    # LangGraph is the single source of truth.
    #
    try:
        # --------------------------------------------------------------
        # INIT STATE (UI → DOMAIN)
        # --------------------------------------------------------------
        initial_state: DecisionState = create_initial_state(
            user_query=question,
        )

        # --------------------------------------------------------------
        # GRAPH EXECUTION
        # --------------------------------------------------------------
        final_state = GRAPH.invoke(initial_state)

        # --------------------------------------------------------------
        # UI FORMATTING (BOUNDARY)
        # --------------------------------------------------------------
        assembler = OutputAssembler()

        (
            _plan,
            _analysis,
            _decision,
            _confidence,
            _messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(final_state)

        try:
            chat_history = messages_to_chatbot(
                final_state.get("messages", [])
            )
        except Exception:
            chat_history = []

        return _map_state_to_ui_outputs(
            state=final_state,
            chat_history=chat_history,
            report_preview=report_preview,
            report_file_path=report_file_path,
            historical_html=historical_html,
            rag_evidence_html=rag_evidence_html,
        )

    except Exception as e:
        return _format_error_output(str(e))


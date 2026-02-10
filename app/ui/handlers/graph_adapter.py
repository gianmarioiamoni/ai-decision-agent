# app/ui/handlers/graph_adapter.py
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
        [],
        error_html,
        None,
        error_html,
        error_html,
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
            plan,
            analysis,
            decision,
            confidence,
            messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(final_state, rag_files)

        raw_messages = final_state.get("messages", [])
        chat_history = messages_to_chatbot(raw_messages)

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
        return _format_error_output(str(e))


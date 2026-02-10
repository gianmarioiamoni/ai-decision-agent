# app/ui/handlers/graph_adapter.py
#
# Graph execution handler (DecisionState-based).
# Streaming-aware, LangGraph-correct, UI-boundary safe.
#

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.components.output_messages import messages_to_chatbot

GRAPH = build_graph()


# ==============================================================================
# Error formatting
# ==============================================================================

def _format_error_output(error_message: str):
    error_msg = f"❌ Error: {error_message}"
    error_html = f"<p style='color: red;'>{error_msg}</p>"
    return (
        error_msg,   # plan
        error_msg,   # analysis
        error_msg,   # decision
        0.0,         # confidence
        [],          # messages
        error_html,  # report preview
        None,        # report file
        error_html,  # historical
        error_html,  # rag evidence
    )


# ==============================================================================
# STREAMING ENTRYPOINT (CORRECT)
# ==============================================================================

def run_graph_streaming(
    question: str,
    rag_files=None,
):
    """
    Executes LangGraph with true streaming.
    Streaming happens at runner level, not inside nodes.
    """

    try:
        # --------------------------------------------------------------
        # INIT STATE (UI → DOMAIN)
        # --------------------------------------------------------------
        initial_state: DecisionState = create_initial_state(
            user_query=question,
        )

        assembler = OutputAssembler()
        last_state: DecisionState | None = None

        # --------------------------------------------------------------
        # STREAM GRAPH EVENTS
        # --------------------------------------------------------------
        for event in GRAPH.stream(initial_state):
            # event: dict[node_name, DecisionState]
            for node_name, state in event.items():
                if not state:
                    continue

                last_state = state

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
                ) = assembler.assemble(state, rag_files)

                raw_messages = state.get("messages", [])
                chat_history = messages_to_chatbot(raw_messages)

                # Yield PARTIAL UI UPDATE
                yield (
                    plan,
                    analysis,
                    decision or "",
                    confidence or 0.0,
                    chat_history,
                    report_preview or "",
                    report_file_path,
                    historical_html or "",
                    rag_evidence_html or "",
                )

        # --------------------------------------------------------------
        # FINAL STATE CHECK
        # --------------------------------------------------------------
        if not last_state:
            raise RuntimeError("Graph did not produce a final state")

        # (Optional) final yield already done in loop – no duplicate needed

    except Exception as e:
        yield _format_error_output(str(e))


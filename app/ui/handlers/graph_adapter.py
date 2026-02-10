# app/ui/handlers/graph_adapter.py
#
# LangGraph streaming adapter – SAFE VERSION
#

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.components.output_messages import messages_to_chatbot
from app.ui.utils.markdown_utils import md_to_plain_text

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
# STREAMING ENTRYPOINT (CORRECT & SAFE)
# ==============================================================================

def run_graph_streaming(
    question: str,
    rag_files=None,
):
    try:
        # --------------------------------------------------------------
        # INIT STATE
        # --------------------------------------------------------------
        initial_state: DecisionState = create_initial_state(
            user_query=question,
        )

        last_state: DecisionState | None = None

        # --------------------------------------------------------------
        # STREAM GRAPH EVENTS
        # --------------------------------------------------------------
        for event in GRAPH.stream(initial_state):
            for node_name, state in event.items():
                if not state:
                    continue

                last_state = state

                # SAFE partial reads (NO assembler here)
                plan = md_to_plain_text(state.get("plan", ""))
                analysis = md_to_plain_text(state.get("analysis", ""))

                yield (
                    plan,
                    analysis,
                    "",     # decision not ready
                    0.0,
                    [],     # messages
                    "",     # report preview
                    None,   # report file
                    "",     # historical
                    "",     # rag evidence
                )

        # --------------------------------------------------------------
        # FINAL ASSEMBLY (STATE IS COMPLETE)
        # --------------------------------------------------------------
        if not last_state:
            raise RuntimeError("Graph did not produce a final state")

        assembler = OutputAssembler()

        (
            plan,
            analysis,
            decision,
            confidence,
            _messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(last_state, rag_files)

        raw_messages = last_state.get("messages", [])
        chat_history = messages_to_chatbot(raw_messages)

        yield (
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
        yield _format_error_output(str(e))

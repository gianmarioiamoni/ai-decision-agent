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
        f"❌ {error_message}",  # phase_indicator 
        error_html,  # report preview
        None,        # report file
        error_html,  # historical
        error_html,  # rag evidence
    )

# ===============================================================================
# Helper Functions - Phase badge and Progress bar
# ===============================================================================

def _phase_from_state(state: DecisionState) -> tuple[str, int]:
    if state.get("decision"):
        return "🟢 **Decision** completed", 3
    if state.get("plan"):
        return "🟣 **Planner** running…", 2
    if state.get("analysis"):
        return "🔵 **Analyzer** running…", 1
    return "⏳ Waiting…", 0


# ==============================================================================
# STREAMING ENTRYPOINT (CORRECT & SAFE)
# ==============================================================================

def run_graph_streaming(
    question: str,
    rag_files=None,
):
    try:
        initial_state = create_initial_state(user_query=question)
        last_state = None

        for state in GRAPH.stream(
            initial_state,
            stream_mode="values"
        ):
            last_state = state

            phase_text, progress = _phase_from_state(state)

            yield (
                md_to_plain_text(state.get("plan") or ""),
                md_to_plain_text(state.get("analysis") or ""),
                "",
                0.0,
                [],
                phase_text,
                progress,
                "",
                None,
                "",
                "",
            )

        if not last_state:
            raise RuntimeError("Graph did not produce a final state")

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
        ) = assembler.assemble(last_state, rag_files)

        yield (
            plan,
            analysis,
            decision,
            confidence,
            messages_to_chatbot(last_state.get("messages", [])),
            "✅ **Workflow completed**",
            3,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    except Exception as e:
        yield _format_error_output(str(e))

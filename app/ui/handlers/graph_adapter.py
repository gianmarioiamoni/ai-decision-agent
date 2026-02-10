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


# ==============================================================================
# STREAMING ENTRYPOINT (CORRECT & SAFE)
# ==============================================================================

def run_graph_streaming(
    question: str,
    rag_files=None,
):
    try:
        initial_state: DecisionState = create_initial_state(
            user_query=question,
        )

        last_state: DecisionState | None = None
        phase_text = "⏳ Starting workflow..."

        # 🔑 QUESTO È IL FIX CHIAVE
        for state in GRAPH.stream(
            initial_state,
            stream_mode="values"
        ):
            last_state = state

            # Phase inference (semplice e robusta)
            if state.get("analysis") and not state.get("plan"):
                phase_text = "🔍 Analyzer running…"
            elif state.get("plan") and not state.get("decision"):
                phase_text = "🗺️ Planner running…"
            elif state.get("decision"):
                phase_text = "✅ Decision completed"

            plan = md_to_plain_text(state.get("plan") or "")
            analysis = md_to_plain_text(state.get("analysis") or "")

            yield (
                plan,          # plan
                analysis,      # analysis
                "",             # decision
                0.0,            # confidence
                [],             # messages
                phase_text,     # phase indicator
                "",             # report preview
                None,           # report file
                "",             # historical
                "",             # rag evidence
            )

        if not last_state:
            raise RuntimeError("Graph did not produce a final state")

        # ---------------- FINAL ASSEMBLY ----------------

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

        chat_history = messages_to_chatbot(
            last_state.get("messages", [])
        )

        yield (
            plan,
            analysis,
            decision,
            confidence,
            chat_history,
            "✅ Workflow completed",
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    except Exception as e:
        yield _format_error_output(str(e))

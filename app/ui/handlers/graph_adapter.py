# app/ui/handlers/graph_adapter.py
#
# LangGraph streaming adapter – FINAL & CORRECT VERSION
#

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.components.output_messages import messages_to_chatbot
from app.ui.utils.markdown_utils import md_to_plain_text

GRAPH = build_graph()


# ==============================================================================
# Error formatting (MUST return EXACTLY the same number of outputs)
# ==============================================================================

def _format_error_output(error_message: str):
    error_msg = f"❌ Error: {error_message}"
    return (
        error_msg,   # plan
        error_msg,   # analysis
        error_msg,   # decision
        0.0,         # confidence
        [],          # messages
        error_msg,   # phase badge
        "",          # progress bar html
        "",          # report preview
        None,        # report file
        "",          # historical
        "",          # rag evidence
    )


# ==============================================================================
# STREAMING ENTRYPOINT (CORRECT)
# ==============================================================================

def run_graph_streaming(
    question: str,
    rag_files=None,
):
    try:
        # --------------------------------------------------------------
        # 1. INIT STATE
        # --------------------------------------------------------------
        initial_state: DecisionState = create_initial_state(
            user_query=question,
        )

        # --------------------------------------------------------------
        # 2. STREAM FOR UX ONLY (NO FINAL STATE HERE)
        # --------------------------------------------------------------
        for event in GRAPH.stream(initial_state):
            event_type = event.get("event")
            node_name = event.get("name")
            state = event.get("state")

            phase_badge = "⏳ Waiting…"
            progress_html = ""

            if event_type == "node_start" and node_name:
                phase_badge = f"▶ **{node_name.upper()}** running…"

            elif event_type == "node_end" and node_name:
                phase_badge = f"✔ **{node_name.upper()}** completed"

            if state:
                yield (
                    md_to_plain_text(state.get("plan") or ""),
                    md_to_plain_text(state.get("analysis") or ""),
                    "",
                    0.0,
                    [],
                    phase_badge,
                    progress_html,
                    "",
                    None,
                    "",
                    "",
                )

        # --------------------------------------------------------------
        # 3. FINAL EXECUTION (THE ONLY SOURCE OF TRUTH)
        # --------------------------------------------------------------
        final_state: DecisionState = GRAPH.invoke(initial_state)

        # --------------------------------------------------------------
        # 4. FINAL ASSEMBLY
        # --------------------------------------------------------------
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
        ) = assembler.assemble(final_state, rag_files)

        chat_history = messages_to_chatbot(final_state.get("messages", []))

        yield (
            plan,
            analysis,
            decision,
            confidence,
            chat_history,
            "✅ **Workflow completed**",
            "",
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    except Exception as e:
        yield _format_error_output(str(e))

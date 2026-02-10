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
        f"❌ {error_message}",  # phase badge (Markdown)
        error_html,  # progress bar (HTML)
        error_html,  # report preview
        None,        # report file
        error_html,  # historical
        error_html,  # rag evidence
    )

# ==============================================================================
# Progress bar renderer (HTML)
# ==============================================================================

def render_progress_bar(phase: str) -> str:
    phases = {
        "intake":   ("10%", "#9ca3af"),
        "analyzer": ("33%", "#3b82f6"),  # blue
        "planner":  ("66%", "#8b5cf6"),  # purple
        "decision": ("100%", "#22c55e"), # green
        "done":     ("100%", "#22c55e"),
    }

    width, color = phases.get(phase, ("10%", "#9ca3af"))

    return f"""
    <div style="width:100%; background:#e5e7eb; border-radius:8px; overflow:hidden;">
      <div style="
        width:{width};
        height:12px;
        background:{color};
        transition: width 0.4s ease, background-color 0.4s ease;
      "></div>
    </div>
    """

# ==============================================================================
# STREAMING ENTRYPOINT
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
        phase_badge = "⏳ **Starting workflow…**"
        progress_bar = render_progress_bar("intake")

        # ------------------------------------------------------------------
        # STREAM GRAPH EVENTS (CORRECT WAY)
        # ------------------------------------------------------------------

        for event in GRAPH.stream(initial_state):
            event_type = event.get("event")
            node_name = event.get("name")
            state = event.get("state")

            if event_type == "node_start" and node_name:
                phase = node_name.lower()
                phase_badge = f"▶ **{node_name.upper()}** running…"
                progress_bar = render_progress_bar(phase)

            elif event_type == "node_end" and node_name:
                phase = node_name.lower()
                phase_badge = f"✔ **{node_name.upper()}** completed"
                progress_bar = render_progress_bar(phase)

            if state:
                last_state = state

                yield (
                    md_to_plain_text(state.get("plan") or ""),
                    md_to_plain_text(state.get("analysis") or ""),
                    "",     # decision not ready
                    0.0,    # confidence not ready
                    [],     # messages
                    phase_badge,
                    progress_bar,
                    "",     # report preview
                    None,   # report file
                    "",     # historical
                    "",     # rag evidence
                )

        # ------------------------------------------------------------------
        # FINAL ASSEMBLY
        # ------------------------------------------------------------------

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
            render_progress_bar("done"),
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    except Exception as e:
        yield _format_error_output(str(e))

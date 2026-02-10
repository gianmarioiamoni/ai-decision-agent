# app/ui/handlers/graph_adapter.py
#
# LangGraph streaming adapter – FINAL WORKING VERSION
#

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.components.output_messages import messages_to_chatbot
from app.ui.utils.markdown_utils import md_to_plain_text

GRAPH = build_graph()

# ------------------------------------------------------------------------------
# Helpers: badge + progress bar
# ------------------------------------------------------------------------------

PHASE_STYLES = {
    "analyzer": ("🔵 **Analyzer** running…", "33%", "#3b82f6"),
    "planner":  ("🟣 **Planner** running…",  "66%", "#8b5cf6"),
    "decision": ("🟢 **Decision** running…", "100%", "#22c55e"),
    "done":     ("✅ **Workflow completed**", "100%", "#22c55e"),
}

def render_progress_bar(width: str, color: str) -> str:
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

# ------------------------------------------------------------------------------
# Error output (11 values EXACTLY)
# ------------------------------------------------------------------------------

def _format_error_output(msg: str):
    return (
        msg, msg, msg, 0.0, [],
        f"❌ {msg}",
        render_progress_bar("100%", "#ef4444"),
        "",
        None,
        "",
        "",
    )

# ------------------------------------------------------------------------------
# STREAMING ENTRYPOINT
# ------------------------------------------------------------------------------

def run_graph_streaming(question: str, rag_files=None):
    try:
        initial_state = create_initial_state(user_query=question)

        phase_badge = "⏳ Waiting…"
        progress_html = render_progress_bar("0%", "#9ca3af")

        last_state: DecisionState | None = None

        # 🔥 IMPORTANT: stream_mode="events"
        for event in GRAPH.stream(initial_state, stream_mode="events"):
            event_type = event["event"]
            node_name = event.get("name")
            state = event.get("state")

            if event_type == "node_start" and node_name in PHASE_STYLES:
                phase_badge, width, color = PHASE_STYLES[node_name]
                progress_html = render_progress_bar(width, color)

            if state:
                last_state = state

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

        if not last_state:
            raise RuntimeError("Graph did not produce a final state")

        # ---------------- FINAL OUTPUT ----------------
        assembler = OutputAssembler()
        (
            plan,
            analysis,
            decision,
            confidence,
            _,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(last_state, rag_files)

        chat_history = messages_to_chatbot(last_state.get("messages", []))

        phase_badge, width, color = PHASE_STYLES["done"]
        progress_html = render_progress_bar(width, color)

        yield (
            plan,
            analysis,
            decision,
            confidence,
            chat_history,
            phase_badge,
            progress_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    except Exception as e:
        yield _format_error_output(str(e))

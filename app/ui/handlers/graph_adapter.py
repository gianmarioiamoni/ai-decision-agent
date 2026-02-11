from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.ui.handlers.formatters.output_assembler import OutputAssembler
from app.ui.components.output_messages import messages_to_chatbot
from app.ui.utils.markdown_utils import md_to_plain_text

GRAPH = build_graph()

# ==============================================================================
# Progress bar
# ==============================================================================

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

PHASES = {
    "analyzer": ("🔵 Analyzer running…", "33%", "#3b82f6"),
    "planner":  ("🟣 Planner running…",  "66%", "#8b5cf6"),
    "decision": ("🟢 Decision running…", "100%", "#22c55e"),
    "done":     ("✅ Workflow completed", "100%", "#22c55e"),
}

# ==============================================================================
# Error output — MUST RETURN 12 STRINGS
# ==============================================================================

def _error_output(msg: str):
    return (
        msg,                     # plan
        msg,                     # analysis
        msg,                     # decision
        "",                      # confidence badge html
        [],                      # messages
        msg,                     # phase badge
        render_progress_bar("0%", "#ef4444"),
        "",                      # report preview
        None,                    # report file
        "",                      # historical
        "",                      # rag evidence
    )

# ==============================================================================
# STREAMING ENTRYPOINT
# ==============================================================================

def run_graph_streaming(question: str, rag_files=None):
    try:
        initial_state = create_initial_state(user_query=question)

        last_state: DecisionState | None = None
        phase_badge = "⏳ Waiting…"
        progress_html = render_progress_bar("5%", "#9ca3af")

        # --------------------------------------------------
        # STREAMING (UX only)
        # --------------------------------------------------
        for state in GRAPH.stream(initial_state, stream_mode="values"):
            last_state = state

            if state.get("analysis") and not state.get("plan"):
                phase_badge, w, c = PHASES["analyzer"]
            elif state.get("plan") and not state.get("decision"):
                phase_badge, w, c = PHASES["planner"]
            elif state.get("decision"):
                phase_badge, w, c = PHASES["decision"]
            else:
                phase_badge, w, c = "⏳ Waiting…", "5%", "#9ca3af"

            progress_html = render_progress_bar(w, c)

            yield (
                md_to_plain_text(state.get("plan") or ""),
                md_to_plain_text(state.get("analysis") or ""),
                "",
                "",
                [],
                phase_badge,
                progress_html,
                "",
                None,
                "",
                "",
            )

        if not last_state:
            raise RuntimeError("No final state produced")

        # --------------------------------------------------
        # FINAL ASSEMBLY
        # --------------------------------------------------
        assembler = OutputAssembler()
        (
            plan,
            analysis,
            decision,
            _confidence_text,
            confidence_badge_html,     # float
            _messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(last_state, rag_files)


        yield (
            plan,
            analysis,
            decision,
            confidence_badge_html,
            messages_to_chatbot(last_state.get("messages", [])),
            PHASES["done"][0],
            render_progress_bar("100%", "#22c55e"),
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    except Exception as e:
        yield _error_output(f"❌ {e}")


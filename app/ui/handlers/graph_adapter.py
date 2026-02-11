# app/ui/handlers/graph_adapter.py
#
# LangGraph streaming adapter – FINAL & COHERENT
#

from app.graph.graph import build_graph
from app.graph.state_factory import create_initial_state
from app.graph.state import DecisionState

from app.ui.handlers.formatters.output_assembler import OutputAssembler, _confidence_badge_html
from app.ui.components.output_messages import messages_to_chatbot
from app.ui.utils.markdown_utils import md_to_plain_text

GRAPH = build_graph()


# ==============================================================================
# Progress bar rendering
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
    "analyzer": (
        '<span class="phase-badge phase-analyzer">🔵 Analyzer running…</span>',
        "33%",
        "#3b82f6",
    ),
    "planner": (
        '<span class="phase-badge phase-planner">🟣 Planner running…</span>',
        "66%",
        "#8b5cf6",
    ),
    "decision": (
        '<span class="phase-badge phase-decision">🟢 Decision running…</span>',
        "100%",
        "#22c55e",
    ),
    "done": (
        '<span class="phase-badge phase-done">✅ Workflow completed</span>',
        "100%",
        "#22c55e",
    ),
}


# ==============================================================================
# Error output
# ==============================================================================

def _error_output(msg: str):
    return (
        msg,
        msg,
        msg,
        {"score": 0.0, "label": "Error"},
        [],
        msg,
        render_progress_bar("0%", "#ef4444"),
        "",
        None,
        "",
        "",
    )


# ==============================================================================
# STREAMING ENTRYPOINT
# ==============================================================================

def run_graph_streaming(question: str, rag_files=None):
    try:
        initial_state = create_initial_state(user_query=question)

        last_state: DecisionState | None = None
        phase_badge = "⏳ Waiting…"
        progress_html = render_progress_bar("0%", "#9ca3af")

        # ----------------------------
        # STREAM (UX only)
        # ----------------------------
        for state in GRAPH.stream(
            initial_state,
            stream_mode="values",
        ):
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
                "",         # decision
                "",         # confidence_text
                "",         # confidence_badge_html
                [],
                phase_badge,
                progress_html,
                "",         # report preview
                None,       # report file
                "",         # historical
                "",         # rag evidence
            )

        if not last_state:
            raise RuntimeError("No final state produced")

        # ----------------------------
        # FINAL ASSEMBLY
        # ----------------------------
        assembler = OutputAssembler()
        (
            plan,
            analysis,
            decision,
            confidence_text,
            _confidence_badge_html,
            _messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        ) = assembler.assemble(last_state, rag_files)

        confidence_score = float(last_state.get("confidence_final", 0.0))
        label = last_state.get("confidence_label") 
        confidence_badge = _confidence_badge_html(confidence_score, label)

        yield (
            plan,
            analysis,
            decision,
            confidence_text,  
            confidence_badge,
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

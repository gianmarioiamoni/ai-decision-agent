# app/ui/handlers/formatters/output_assembler.py

from app.graph.state import DecisionState

from .message_formatter import MessageFormatter
from .historical_formatter import HistoricalFormatter
from app.ui.utils.rag_formatter import format_rag_context_for_ui
from app.ui.handlers.formatters.text_normalizer import normalize_markdown_to_text


# --------------------------------------------------
# Safe numeric extraction
# --------------------------------------------------


def _safe_float(value, default: float) -> float:
    if value is None:
        return default
    if isinstance(value, list):
        if not value:
            return default
        return float(value[0])
    return float(value)


# --------------------------------------------------
# Confidence helpers
# --------------------------------------------------


def _confidence_label(score: float) -> str:
    if score >= 0.8:
        return "High"
    elif score >= 0.6:
        return "Medium"
    return "Low"


def _confidence_badge_html(
    score: float,
    label: str,
    base: float,
    factor: float,
) -> str:

    color_map = {
        "High": "#22c55e",
        "Medium": "#f59e0b",
        "Low": "#ef4444",
    }

    color = color_map.get(label, "#9ca3af")

    tooltip_html = f"""
    <div style="
        background:#111827;
        color:white;
        padding:10px 12px;
        border-radius:8px;
        font-size:12px;
        line-height:1.4;
        box-shadow:0 4px 12px rgba(0,0,0,0.25);
        min-width:200px;
    ">
        <div><strong>Confidence Breakdown</strong></div>
        <div>Base: {base:.2f}</div>
        <div>Historical factor: {factor:.2f}</div>
        <div style="margin-top:4px;"><strong>Final: {score:.2f}</strong></div>
    </div>
    """

    return f"""
    <div style="
        display:inline-flex;
        align-items:center;
        gap:10px;
        position:relative;
    ">
        <span style="
            padding:4px 10px;
            border-radius:9999px;
            background:{color};
            color:white;
            font-weight:600;
        ">
            {label}
        </span>

        <span style="color:#6b7280;">
            {score:.2f}
        </span>

        <div style="position:relative; display:inline-block;">
            <span style="
                font-weight:600;
                cursor:pointer;
                color:#6b7280;
            "
            onmouseover="this.nextElementSibling.style.display='block'"
            onmouseout="this.nextElementSibling.style.display='none'"
            >
                ℹ
            </span>

            <div style="
                display:none;
                position:absolute;
                top:24px;
                left:0;
                z-index:1000;
            ">
                {tooltip_html}
            </div>
        </div>
    </div>
    """


class OutputAssembler:

    # --------------------------------------------------
    # Facade for assembling Gradio UI output
    # --------------------------------------------------

    def __init__(self) -> None:
        self.message_formatter = MessageFormatter()
        self.historical_formatter = HistoricalFormatter()

    def assemble(
        self,
        state: DecisionState,
        context_docs,
    ):

        # ----------------------------
        # Textual outputs
        # ----------------------------

        plan = normalize_markdown_to_text(state.get("plan") or "No plan generated")

        analysis = normalize_markdown_to_text(
            state.get("analysis") or "No analysis generated"
        )

        decision = normalize_markdown_to_text(
            state.get("decision") or "No decision generated"
        )

        # ----------------------------
        # Confidence (SAFE)
        # ----------------------------

        confidence_score = _safe_float(state.get("confidence_final"), 0.0)

        confidence_base = _safe_float(state.get("confidence_base"), 0.0)

        historical_factor = _safe_float(state.get("historical_factor"), 1.0)

        confidence_label = state.get("confidence_label") or _confidence_label(
            confidence_score
        )

        confidence_badge_html = _confidence_badge_html(
            score=confidence_score,
            label=confidence_label,
            base=confidence_base,
            factor=historical_factor,
        )

        # ----------------------------
        # Messages
        # ----------------------------

        messages_html = self.message_formatter.format(state.get("messages", []))

        # ----------------------------
        # Report
        # ----------------------------

        report_preview, report_file_path = self._format_report(state)

        # ----------------------------
        # Historical + RAG
        # ----------------------------

        historical_html = (
            self.historical_formatter.format(state["similar_decisions"])
            if state.get("similar_decisions")
            else ""
        )

        rag_evidence_html = format_rag_context_for_ui(
            context_docs,
            state.get("authoritative_context"),
        )

        return (
            plan,
            analysis,
            decision,
            confidence_badge_html,
            messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    # --------------------------------------------------
    # Report
    # --------------------------------------------------

    def _format_report(self, state):

        from app.report.session_report import (
            generate_preview_html,
            generate_session_report,
        )

        from app.ui.handlers.report_format_handler import (
            get_initial_report_file,
        )

        try:
            report_preview = generate_preview_html(state)
            report_html = generate_session_report(state)
            report_file_path = get_initial_report_file(report_html)
        except Exception:
            report_preview = "<p style='color: orange;'>⚠️ Report generation failed</p>"
            report_file_path = None

        return report_preview, report_file_path

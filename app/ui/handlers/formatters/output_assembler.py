# app/ui/handlers/formatters/output_assembler.py

from app.graph.state import DecisionState

from .message_formatter import MessageFormatter
from .historical_formatter import HistoricalFormatter
from app.ui.utils.rag_formatter import format_rag_context_for_ui
from app.ui.handlers.formatters.text_normalizer import normalize_markdown_to_text


class OutputAssembler:
    #
    # Facade for assembling Gradio UI output from DecisionState.
    #
    # Responsibilities:
    # - Convert domain state into UI-ready artifacts
    # - NO domain logic
    # - NO recomputation
    #

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
        plan = normalize_markdown_to_text(
            state.get("plan") or "No plan generated"
        )
        analysis = normalize_markdown_to_text(
            state.get("analysis") or "No analysis generated"
        )
        decision = normalize_markdown_to_text(
            state.get("decision") or "No decision generated"
        )

        # ----------------------------
        # Confidence (DOMAIN → UI)
        # ----------------------------
        confidence_score = float(state.get("confidence_final") or 0.0)
        confidence_label = state.get("confidence_label") or "Unknown"

        confidence = {
            "score": confidence_score,
            "label": confidence_label,
        }

        # ----------------------------
        # Messages
        # ----------------------------
        messages_html = self.message_formatter.format(
            state.get("messages", [])
        )

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
            confidence,          # ⬅️ STRUCTURED
            messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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
            report_preview = (
                "<p style='color: orange;'>⚠️ Report generation failed</p>"
            )
            report_file_path = None

        return report_preview, report_file_path

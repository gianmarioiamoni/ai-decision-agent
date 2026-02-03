# app/ui/handlers/formatters/output_assembler.py
#
# Assembles UI output from DecisionState.
#
# STEP 0.4.3:
# - Consume DecisionState directly
# - Remove dict-based result access
# - UI becomes a pure projection of domain state
#

from app.graph.state import DecisionState

from .message_formatter import MessageFormatter
from .historical_formatter import HistoricalFormatter
from app.ui.utils.markdown_utils import md_to_plain_text
from app.ui.utils.rag_formatter import format_rag_context_for_ui
from app.ui.handlers.report_format_handler import get_initial_report_file


class OutputAssembler:
    #
    # Facade for assembling Gradio UI output from DecisionState.
    #
    # Responsibility:
    # - Convert domain state into UI-ready artifacts
    # - Coordinate specialized formatters
    #

    def __init__(self) -> None:
        self.message_formatter = MessageFormatter()
        self.historical_formatter = HistoricalFormatter()

    def assemble(
        self,
        state: DecisionState,
        context_docs,
    ):
        #
        # Assemble UI outputs from DecisionState.
        #
        # Returns:
        # Tuple of outputs expected by Gradio UI.
        #

        plan = self._to_plain_text(state["plan"], "No plan generated")
        analysis = self._to_plain_text(state["analysis"], "No analysis generated")
        decision = self._to_plain_text(state["decision"], "No decision generated")

        confidence = float(state["confidence_final"] or 0.0)

        messages_html = self.message_formatter.format(
            state["messages"]
        )

        report_preview, report_file_path = self._format_report(state)

        historical_html = self.historical_formatter.format(
            state["similar_decisions"]
        ) if state["similar_decisions"] else ""

        rag_evidence_html = format_rag_context_for_ui(
            context_docs,
            state["authoritative_context"],
        )

        return (
            plan,
            analysis,
            decision,
            confidence,
            messages_html,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _to_plain_text(
        self,
        value: str | None,
        default: str,
    ) -> str:
        markdown = value or default
        return md_to_plain_text(markdown)

    def _format_report(self, state):
        from app.report.session_report import generate_preview_html, generate_session_report
        from app.ui.handlers.report_format_handler import get_initial_report_file

        try:
            report_preview = generate_preview_html(state)
            report_html = generate_session_report(state)
            report_file_path = get_initial_report_file(report_html)
        except Exception as e:
            report_preview = (
                "<p style='color: orange;'>⚠️ Report generation failed</p>"
            )
            report_file_path = None
        return report_preview, report_file_path



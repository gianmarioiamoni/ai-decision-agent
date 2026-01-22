# app/ui/handlers/formatters/output_assembler.py
#
# Coordinates all formatters to assemble complete UI output.
# Facade pattern for formatting complexity.
#

from typing import Tuple, Optional, List

from .message_formatter import MessageFormatter
from .historical_formatter import HistoricalFormatter
from app.ui.utils.markdown_utils import md_to_plain_text
from app.ui.utils.rag_formatter import format_rag_context_for_ui


class OutputAssembler:
    #
    # Assembles formatted outputs from graph results for Gradio UI.
    #
    # Responsibility: Coordinate formatters and assemble final output tuple.
    # Follows Facade pattern to hide formatting complexity.
    #
    
    def __init__(self):
        """Initialize all formatters."""
        self.message_formatter = MessageFormatter()
        self.historical_formatter = HistoricalFormatter()
    
    def assemble(
        self,
        result: dict,
        context_docs: List[str]
    ) -> Tuple[str, str, str, float, str, str, Optional[str], str, str]:
        # Assemble complete UI output from graph result.
        #
        # Args:
        #     result: Graph execution result dictionary
        #     context_docs: Context documents used in execution
        #
        # Returns:
        #     Tuple of 9 outputs for Gradio UI:
        #     - plan (str): Formatted plan text
        #     - analysis (str): Formatted analysis text
        #     - decision (str): Formatted decision text
        #     - confidence (float): Confidence score (0.0-1.0)
        #     - messages (str): HTML-formatted conversation log
        #     - report_preview (str): HTML preview of session report
        #     - report_file_path (str | None): Path to downloadable HTML report
        #     - historical_html (str): HTML-formatted similar historical decisions
        #     - rag_evidence_html (str): HTML-formatted RAG context and evidence
        #

        # Extract and convert markdown outputs to plain text
        plan = self._extract_and_convert(result, "plan", "No plan generated")
        analysis = self._extract_and_convert(result, "analysis", "No analysis generated")
        decision = self._extract_and_convert(result, "decision", "No decision generated")
        
        # Extract confidence score
        confidence_val = self._extract_confidence(result)
        
        # Format messages using dedicated formatter
        messages = self.message_formatter.format(result.get("messages", []))
        
        # Format report outputs
        report_preview, report_file_path = self._format_report(result)
        
        # Format historical decisions using dedicated formatter
        historical_html = self.historical_formatter.format(
            result.get("similar_decisions", [])
        )
        
        # Format RAG evidence using existing utility
        rag_context = result.get("rag_context", "")
        rag_evidence_html = format_rag_context_for_ui(context_docs, rag_context)
        
        return (
            plan,
            analysis,
            decision,
            confidence_val,
            messages,
            report_preview,
            report_file_path,
            historical_html,
            rag_evidence_html
        )
    
    def _extract_and_convert(
        self,
        result: dict,
        key: str,
        default: str
    ) -> str:
        # Extract markdown field and convert to plain text.
        #
        # Args:
        #     result: Result dictionary
        #     key: Field key to extract
        #     default: Default value if key not found
        #
        # Returns:
        #     Plain text version of markdown content
        #
        
        markdown = result.get(key) or default
        return md_to_plain_text(markdown)
    
    def _extract_confidence(self, result: dict) -> float:
        # Extract and validate confidence score.
        #
        # Args:
        #     result: Result dictionary
        #
        # Returns:
        #     Confidence value as float (0.0 if not present)
        #
        confidence_val = result.get("confidence")
        return float(confidence_val) if confidence_val is not None else 0.0
    
    def _format_report(self, result: dict) -> Tuple[str, Optional[str]]:
        # Format report HTML and save to temporary file.
        #
        # Args:
        #     result: Result dictionary
        #
        # Returns:
        #     Tuple of (report_preview_html, report_file_path)
        #
        from app.ui.handlers.report_format_handler import get_initial_report_file
        
        report_html = result.get("report_html") or (
            "<p style='color: orange;'>⚠️ No report generated</p>"
        )
        report_preview = result.get("report_preview") or report_html
        
        # Use the new handler that caches HTML for format changes
        report_file_path = get_initial_report_file(report_html)
        
        return report_preview, report_file_path


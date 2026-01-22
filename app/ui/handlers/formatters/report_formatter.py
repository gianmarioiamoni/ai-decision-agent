# app/ui/handlers/formatters/report_formatter.py
#
# ReportFormatter - Formats session report preview
#

from .base_formatter import BaseFormatter


class ReportFormatter(BaseFormatter):
    """
    Formats session report preview for display.
    
    Responsibilities:
    - Extract report preview from result
    - Return formatted HTML preview
    
    Does NOT handle:
    - Report HTML generation (done by report module)
    - File saving (done by utils/file_io.py)
    """
    
    def format(self, report_html: str) -> str:
        """
        Format report HTML for preview display.
        
        Args:
            report_html: Complete HTML report
        
        Returns:
            HTML preview string (or warning message)
        """
        if not report_html or report_html.strip() == "":
            return '<p style="color: gray;">📄 No report generated yet</p>'
        
        # Check if this is a warning/error message (not actual HTML)
        if not report_html.strip().startswith("<"):
            # It's a plain text warning, wrap it in HTML
            return f'<p style="color: orange;">⚠️ {report_html}</p>'
        
        # Return the actual HTML report preview
        return report_html


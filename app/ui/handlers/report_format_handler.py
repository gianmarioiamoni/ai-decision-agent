# app/ui/handlers/report_format_handler.py
#
# Report Format Handler - Manages report format changes in UI.
#

from app.ui.components.output_report import save_report_for_download


# Store the last generated report HTML (simple in-memory cache)
_last_report_html = None


def cache_report_html(report_html):
    #
    # Cache the report HTML for format conversion.
    #
    # Args:
    #     report_html: HTML content to cache
    #
    global _last_report_html
    _last_report_html = report_html
    print(f"[REPORT] 📝 Cached report HTML ({len(report_html)} chars)")


def handle_format_change(format_type):
    #
    # Handle format selection change and regenerate download file.
    #
    # Args:
    #     format_type: Selected format ("HTML" or "PDF")
    #
    # Returns:
    #     Path to the new temporary file in the selected format
    #
    global _last_report_html
    
    print(f"\n[REPORT] 📥 Format changed to: {format_type}")
    
    if _last_report_html is None:
        print(f"[REPORT] ⚠️ No report available yet")
        return None
    
    try:
        file_path = save_report_for_download(_last_report_html, format_type)
        print(f"[REPORT] ✅ Generated {format_type} report: {file_path}")
        return file_path
    
    except Exception as e:
        print(f"[REPORT] ❌ Failed to generate {format_type} report: {e}")
        return None


def get_initial_report_file(report_html):
    #
    # Generate initial report file (HTML format by default) and cache HTML.
    #
    # Args:
    #     report_html: HTML content of the report
    #
    # Returns:
    #     Path to the temporary HTML file
    #
    
    # Only cache valid reports (not warning messages)
    if report_html and not report_html.startswith("<p style='color: orange;'>"):
        cache_report_html(report_html)
        # Generate initial HTML file
        return save_report_for_download(report_html, "HTML")
    
    # Don't generate file for invalid/warning reports
    return None


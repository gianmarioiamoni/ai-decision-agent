# app/ui/components/output_report.py
# Gradio component for displaying and downloading the HTML session report

import gradio as gr
from typing import Tuple
import tempfile

def create_output_report():
    # Creates a modular Gradio output component for session report.
    #
    # Returns:
    #     report_html_component: HTML preview of report
    #     format_selector: Radio button to select download format (HTML/PDF)
    #     report_download_component: File download button
    
    # HTML preview component (dynamic)
    report_html_component = gr.HTML(
        label=None,  # No internal label - using external section title with icon
        value="",  # Explicit empty string instead of None
        show_label=False
    )

    # Format selector
    format_selector = gr.Radio(
        choices=["HTML", "PDF", "DOCX"],
        value="HTML",
        label=None,
        info="Select the format for downloading the report",
        show_label=False
    )

    # File download component  
    report_download_component = gr.File(
        label=None,  # No internal label - using external section title with icon
        file_count="single",
        file_types=[".html", ".pdf", ".docx"],
        type="filepath",
        interactive=False,  # Disable upload
        show_label=False
        # Note: value not specified for File components (Gradio default behavior)
    )

    return report_html_component, format_selector, report_download_component


def save_report_for_download(report_html: str, format_type: str = "HTML") -> str:
    # Save the report to a temporary file in the specified format.
    #
    # Args:
    #     report_html: HTML content of the report
    #     format_type: "HTML", "PDF", or "DOCX"
    #
    # Returns:
    #     Path to the temporary file
    #
    
    if format_type.upper() == "PDF":
        from app.report.pdf_converter import create_temp_pdf
        
        try:
            pdf_path = create_temp_pdf(report_html)
            if pdf_path:
                print(f"[REPORT] ✅ PDF report saved: {pdf_path}")
                return pdf_path
            else:
                # Fallback to HTML if PDF conversion fails
                print(f"[REPORT] ⚠️ PDF conversion failed, falling back to HTML")
                format_type = "HTML"
        except ImportError as e:
            print(f"[REPORT] ⚠️ {e}")
            print(f"[REPORT] ⚠️ Falling back to HTML format")
            format_type = "HTML"
    
    elif format_type.upper() == "DOCX":
        from app.report.docx_converter import create_temp_docx
        
        try:
            docx_path = create_temp_docx(report_html)
            if docx_path:
                print(f"[REPORT] ✅ DOCX report saved: {docx_path}")
                return docx_path
            else:
                # Fallback to HTML if DOCX conversion fails
                print(f"[REPORT] ⚠️ DOCX conversion failed, falling back to HTML")
                format_type = "HTML"
        except ImportError as e:
            print(f"[REPORT] ⚠️ {e}")
            print(f"[REPORT] ⚠️ Falling back to HTML format")
            format_type = "HTML"
    
    # Save as HTML (default or fallback)
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html",
        mode="w",
        encoding="utf-8"
    ) as tmp_file:
        tmp_file.write(report_html)
        print(f"[REPORT] ✅ HTML report saved: {tmp_file.name}")
        return tmp_file.name

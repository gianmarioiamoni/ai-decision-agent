# app/ui/components/report_download_section.py
#
# Report Download Section Component
# Displays the format selector and download button

import gradio as gr


def create_report_download_section(format_selector, report_download_output):
    #
    # Create the report download section with format selector.
    #
    # Args:
    #     format_selector: gr.Radio component for format selection
    #     report_download_output: gr.File component for download
    #
    # Returns:
    #     Column component with download section
    #
    
    with gr.Column(scale=1) as col:
        gr.Markdown("### 💾 Download Report")
        # Add spacing to align with Question box in preview
        # Increased by one line (from 45px to ~70px)
        gr.Markdown("<div style='margin-top: 70px;'></div>")
        gr.Markdown("**📥 Download Format**")
        format_selector.render()
        report_download_output.render()
    
    return col


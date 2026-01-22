# app/ui/components/report_preview_section.py
#
# Report Preview Section Component
# Displays the scrollable preview of the session report

import gradio as gr


def create_report_preview_section(report_output):
    #
    # Create the report preview section with scrollable container.
    #
    # Args:
    #     report_output: gr.HTML component for report preview
    #
    # Returns:
    #     Column component with preview section
    #
    
    with gr.Column(scale=2, elem_id="report-preview-column") as col:
        gr.Markdown("### 📄 Session Report Preview")
        # Wrapper with fixed height and scroll (scrollbar hidden)
        gr.HTML("""
        <style>
            #report-preview-wrapper {
                max-height: 600px;
                overflow-y: auto;
                overflow-x: hidden;
                padding-right: 10px;
            }
            /* Hide scrollbar but keep functionality */
            #report-preview-wrapper::-webkit-scrollbar {
                width: 0px;
                background: transparent;
            }
            /* For Firefox */
            #report-preview-wrapper {
                scrollbar-width: none;
            }
            /* For IE and Edge */
            #report-preview-wrapper {
                -ms-overflow-style: none;
            }
        </style>
        <div id="report-preview-wrapper-start"></div>
        """)
        with gr.Column(elem_id="report-preview-wrapper"):
            report_output.render()
    
    return col


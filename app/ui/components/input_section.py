# app/ui/components/input_section.py
#
# Input section component.
#
# This module provides the complete input section for the AI Decision Support Agent UI,
# including the question input, submit button, and RAG file upload.
#

import gradio as gr
from typing import Tuple

from .input_question import create_input_question
from .rag_file_manager_ui import create_rag_file_input, create_rag_file_manager


def create_input_section(
    subtitle_color: str = "#a0aec0"
) -> Tuple:
    # Create the complete input section with question input and RAG upload.
    #
    # This function creates a two-column layout:
    # - Left: Question input and submit button
    # - Right: Optional RAG context documents upload (collapsible)
    #           Including stored files management
    #
    # Args:
    #     subtitle_color: Hex color code for hints and descriptions
    #
    # Returns:
    #     Tuple of (question_input, submit_button, rag_input, upload_status_output,
    #              storage_summary, files_list_display, refresh_files_btn, 
    #              clear_files_btn, clear_status_display)
    #

    # Top row with description
    gr.Markdown(
        f"<p style='color:{subtitle_color}; font-size:0.95em; margin-bottom:10px;'>"
        "🤖 The agent will plan, research, analyze, and provide a reasoned decision."
        "</p>"
    )
    
    # Main input row
    with gr.Row():
        with gr.Column(scale=1):
            # Input section title with icon
            gr.Markdown("### ❓ Your Query")
            question_input, submit_button = create_input_question()
        
        with gr.Column(scale=1):
            # Tip aligned with the question title
            gr.Markdown(
                f"<p style='color:{subtitle_color}; font-size:0.95em; margin-bottom:10px;'>"
                "💡 Tip: Upload context documents to ground the analysis in your specific organizational reality."
                "</p>"
            )
            
            # RAG context file upload - collapsible accordion
            with gr.Accordion("📂 Optional Context Documents", open=False):
                rag_input = create_rag_file_input()
                upload_status_output = gr.Markdown("", visible=False)
                
                gr.Markdown("---")
                
                # Stored files management - nested section
                gr.Markdown("### 🗂️ Manage Stored Context Files")
                (
                    storage_summary,
                    files_list_display,
                    refresh_files_btn,
                    clear_files_btn,
                    clear_status_display,
                    _  # Ignore duplicate upload_status_output
                ) = create_rag_file_manager()
    
    return (question_input, submit_button, rag_input, upload_status_output,
            storage_summary, files_list_display, refresh_files_btn,
            clear_files_btn, clear_status_display)


# app/ui/components/rag_file_manager_ui.py
#
# RAG File Manager UI Components - Simple Event-Driven Pattern.
#
# This module provides the RAG file manager UI components,
# including the RAG file input and management buttons.
#

import gradio as gr
from typing import Tuple

from app.rag.file_manager import get_file_manager

# Get singleton instance for initial values
file_manager = get_file_manager()


def create_rag_file_input():
    # Create the RAG file input component.
    #
    # Returns:
    #     gr.File: Gradio file input component for uploading context documents
    #

    # Title with icon - aligned with input box below
    gr.Markdown(
        "<h3 style='margin-left: 0.5rem;'>📤 Upload Documents</h3>"
    )
    
    rag_input = gr.File(
        file_types=[".txt", ".md", ".csv"],
        file_count="multiple",
        label=None,  # No internal label - using external title
        show_label=False
        # Note: value not specified for File upload components (Gradio default behavior)
    )
    return rag_input


def create_rag_file_manager() -> Tuple:
    # Create the complete RAG file management UI.
    #
    # Returns:
    #     Tuple of UI components
    #
    
    # Info text about persistence
    gr.Markdown(
        "<p style='color:#94a3b8; font-size:0.9em;'>"
        "Files uploaded here are stored permanently and used for all future questions until cleared.<br>"
        "This allows you to refresh the page without losing your context documents."
        "</p>"
    )
    
    print("\n" + "🏗️"*35)
    print("🏗️ CREATING RAG File Manager Components (Simple Pattern)")
    print("🏗️"*35)
    
    # Get initial values
    initial_summary = file_manager.render_storage_summary()
    initial_files_text = file_manager.render_files_text()
    
    print(f"✅ Initial storage summary: {initial_summary}")
    print(f"✅ Initial files text: {len(initial_files_text)} chars")
    
    # Storage summary (always visible)
    storage_summary = gr.Markdown(initial_summary)
    
    # Title with icon for file list - aligned with textbox below
    gr.Markdown(
        "<h3 style='margin-left: 0.5rem;'>📂 Stored Files</h3>"
    )
    
    # File list display (always visible)
    files_list_display = gr.Textbox(
        label=None,  # No internal label - using external title
        value=initial_files_text,
        interactive=False,
        lines=6,
        max_lines=10,
        show_label=False
    )
    
    # Management buttons
    with gr.Row():
        refresh_files_btn = gr.Button("🔄 Refresh List", size="sm", scale=1)
        clear_files_btn = gr.Button("🗑️ Clear All Files", size="sm", variant="stop", scale=1)
    
    # Status displays
    clear_status_display = gr.Markdown("", visible=False)
    upload_status_output = gr.Markdown("", visible=False)
    
    print("✅ All components created")
    print("🏗️"*35 + "\n")
    
    return (
        storage_summary,
        files_list_display,
        refresh_files_btn,
        clear_files_btn,
        clear_status_display,
        upload_status_output
    )

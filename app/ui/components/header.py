# app/ui/components/header.py
#
# Application header component.
#
# This module provides the header section for the AI Decision Support Agent UI,
# including title and description.
#

import gradio as gr


def create_header(title_color: str = "#ffffff", subtitle_color: str = "#a0aec0") -> None:
    # Create the application header with title and description.
    #
    # Args:
    #     title_color: Hex color code for the title
    #     subtitle_color: Hex color code for the subtitle/description
    #
    gr.Markdown(
        f"""
        # 🤖 AI Decision Support Agent
        <p style='color:{subtitle_color}; font-size:1.1em; margin-top:0;'>
        Analyze complex decisions with confidence scores, historical context, and RAG-powered evidence.
        </p>
        """
    )


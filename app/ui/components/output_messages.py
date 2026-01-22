# app/ui/components/output_messages.py

import gradio as gr

# Responsibility: display messages log
def create_output_messages():
    messages_output = gr.Textbox(
        label=None,  # No internal label - using external section title with icon
        placeholder="Messages from the agent will appear here",
        interactive=False,
        lines=20,  # Increased lines for better readability
        max_lines=40,  # Allow expansion for long conversations
        show_label=False
    )
    return messages_output

# app/ui/components/input_question.py

import gradio as gr

# Responsibility: provide input field for user's question
def create_input_question():
    question_input = gr.Textbox(
        label=None,  # No internal label - using external section title with icon
        placeholder="E.g. Should our team adopt LangGraph?",
        lines=3,  # More space for input
        submit_btn=False,  # Hide submit button icon (Enter key still works via question_input.submit())
        show_label=False
    )
    submit_button = gr.Button("🚀 Analyse", variant="primary", size="lg", min_width=120, scale=0)
    return question_input, submit_button

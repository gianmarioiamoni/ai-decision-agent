# app/ui/components/output_decision.py
# Responsibility: display final decision and confidence with semantic color badge

import gradio as gr




def create_output_decision():
    # Decision text
    decision_output = gr.Textbox(
        value="",
        placeholder="Final decision will appear here",
        interactive=False,
        lines=12,
        show_label=False,
    )


    confidence_badge = gr.HTML(
        value="",
        show_label=False,
    )

    return decision_output, confidence_badge

# /app/ui/components/output_decision.py
# Responsibility: display final decision and confidence with enhanced UI (badge + tooltip)

import gradio as gr

# Color thresholds for confidence badge
def get_confidence_color(confidence: int) -> str:
    if confidence >= 85:
        return "green"
    elif confidence >= 60:
        return "orange"
    else:
        return "red"

def create_output_decision():
    # Creates Gradio components for displaying final decision and confidence.
    # Includes color-coded badge for confidence and tooltips explaining each field.
    
    # Decision textbox
    decision_output = gr.Textbox(
        label="decision_output",
        value="",
        placeholder="Final decision will appear here",
        interactive=False,
        lines=15,
        max_lines=25,
        show_label=False
    )

    # Confidence badge (rendered as a Textbox with color info)
    confidence_output = gr.Textbox(
        label="confidence_output",
        value="",
        placeholder="Confidence will appear here (0-100)",
        interactive=False,
        lines=1,
        show_label=False
    )

    return decision_output, confidence_output

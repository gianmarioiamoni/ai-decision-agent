# app/ui/components/output_decision.py
# Responsibility: display final decision and confidence with semantic color badge

import gradio as gr


def _confidence_badge_html(
    score: float,
    label: str,
) -> str:
    color_map = {
        "High": "#22c55e",    # green
        "Medium": "#f59e0b",  # orange
        "Low": "#ef4444",     # red
    }

    color = color_map.get(label, "#9ca3af")  # fallback gray

    return f"""
    <div style="
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
    ">
        <span style="
            padding: 4px 10px;
            border-radius: 9999px;
            background-color: {color};
            color: white;
            font-weight: 600;
        ">
            {label}
        </span>
        <span style="color: #6b7280;">
            {score:.2f}
        </span>
    </div>
    """


def create_output_decision():
    # Decision text
    decision_output = gr.Textbox(
        value="",
        placeholder="Final decision will appear here",
        interactive=False,
        lines=12,
        show_label=False,
    )

    # Confidence badge rendered as HTML
    confidence_output = gr.HTML(
        value="",
        label="Confidence",
    )

    return decision_output, confidence_output

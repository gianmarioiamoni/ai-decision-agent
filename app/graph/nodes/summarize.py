# app/graph/nodes/summarize.py
# Final summarization node and session report generation

from typing import Dict
from app.graph.state import DecisionState
from app.report.session_report import generate_session_report, generate_preview_html

# Summarize node
# This node compresses message history and generates a final session report
def summarize_node(state: DecisionState) -> Dict:
    #
    # Summarize node:
    # - Compresses message history to manage context length
    # - Generates a final HTML session report
    #
    # Args:
    #     state: DecisionState containing messages
    #
    # Returns:
    #     Dict containing updated messages and report_html
    #

    messages = state.get("messages", [])
    MAX_MESSAGES = 10

    updates: Dict = {}

    # -----------------------------
    # Message compression logic
    # -----------------------------
    if len(messages) > MAX_MESSAGES:
        # Keep first message (original question) and last N-1 messages
        compressed_messages = [messages[0]] + messages[-(MAX_MESSAGES - 1):]

        updates["messages"] = compressed_messages + [
            {
                "role": "assistant",
                "content": (
                    f"[Compressed message history: kept "
                    f"{len(compressed_messages)} of {len(messages)} messages]"
                )
            }
        ]

    # -----------------------------
    # Session report generation
    # -----------------------------
    # Generate full HTML report for download
    report_html = generate_session_report(state)
    updates["report_html"] = report_html
    
    # Generate preview HTML for Gradio (without html/head/body wrapper)
    preview_html = generate_preview_html(state)
    updates["report_preview"] = preview_html

    return updates


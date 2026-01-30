# app/ui/components/output_messages.py

import gradio as gr

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def render_messages_as_text(messages) -> str:
    if not messages:
        return ""

    blocks = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            blocks.append(f"💬 USER:\n{msg.content}")
        elif isinstance(msg, AIMessage):
            blocks.append(f"🤖 ASSISTANT:\n{msg.content}")
        elif isinstance(msg, SystemMessage):
            blocks.append(f"⚙️ SYSTEM:\n{msg.content}")
        else:
            # Fallback for safety
            blocks.append(str(msg))

    # Double newline = visual separation
    return "\n\n" + ("\n\n" + "-" * 40 + "\n\n").join(blocks)


def create_output_messages():
    messages_output = gr.Textbox(
        label="messages_output",  # No internal label - using external section title with icon
        value="",  # Explicit empty string instead of None
        placeholder="Messages from the agent will appear here",
        interactive=False,
        lines=20,  # Increased lines for better readability
        max_lines=40,  # Allow expansion for long conversations
        show_label=False
    )
    return messages_output
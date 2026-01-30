# app/ui/components/output_messages.py

import gradio as gr

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages import HumanMessage, AIMessage

def messages_to_chatbot(messages):
    chat = []
    current_user = None

    for msg in messages:
        if isinstance(msg, HumanMessage):
            current_user = msg.content
        elif isinstance(msg, AIMessage):
            chat.append((current_user, msg.content))
            current_user = None

    return chat


def create_output_messages():
    messages_output = gr.Chatbot(
        label="Conversation History",  # No internal label - using external section title with icon
        show_label=False,
        height=400,
    )
    return messages_output
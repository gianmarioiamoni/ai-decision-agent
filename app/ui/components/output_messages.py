# app/ui/components/output_messages.py

import gradio as gr

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages import HumanMessage, AIMessage

def messages_to_chatbot(messages):
    chat = []

    for msg in messages:
        if isinstance(msg, HumanMessage):
            chat.append({
                "role": "user",
                "content": msg.content
            })
        elif isinstance(msg, AIMessage):
            chat.append({
                "role": "assistant",
                "content": msg.content
            })
        elif isinstance(msg, SystemMessage):
            chat.append({
                "role": "system",
                "content": msg.content
            })

    return chat


def create_output_messages():
    messages_output = gr.Chatbot(
        label="Conversation History",  # No internal label - using external section title with icon
        show_label=False,
        height=400,
    )
    return messages_output
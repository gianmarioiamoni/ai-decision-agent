# app/ui/components/output_messages.py

import gradio as gr

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages import HumanMessage, AIMessage

def messages_to_chatbot(messages):
    chatbot_messages = []

    if not messages:
        return chatbot_messages

    for msg in messages:
        try:
            # Handle dict messages (fallback)
            if isinstance(msg, dict):
                if "role" in msg and "content" in msg:
                    # Ensure role is valid (user or assistant)
                    role = msg["role"]
                    if role not in ["user", "assistant"]:
                        role = "assistant"
                    chatbot_messages.append({
                        "role": role,
                        "content": str(msg["content"])
                    })
                continue
                
            # Handle LangChain message objects
            if isinstance(msg, HumanMessage):
                chatbot_messages.append({
                    "role": "user",
                    "content": str(msg.content)
                })
            elif isinstance(msg, AIMessage):
                chatbot_messages.append({
                    "role": "assistant",
                    "content": str(msg.content)
                })
            elif isinstance(msg, SystemMessage):
                chatbot_messages.append({
                    "role": "assistant",  # Gradio doesn't support system role
                    "content": str(msg.content)
                })
        except Exception as e:
            print(f"⚠️ Error processing message: {e}")
            continue

    return chatbot_messages


def create_output_messages():
    messages_output = gr.Chatbot(
        label="Conversation History",  # No internal label - using external section title with icon
        show_label=False,
        type="messages",
        height=400,
    )
    return messages_output
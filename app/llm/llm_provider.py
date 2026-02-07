# app/llm/llm_provider.py

from langchain_openai import ChatOpenAI


def get_llm():
    #
    # Centralized factory for planner LLM.
    # Overridable in tests.
    #
    return ChatOpenAI(
        temperature=0.2,
        model="gpt-4o-mini",
    )

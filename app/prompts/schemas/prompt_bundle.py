# app/prompts/schemas/prompt_bundle.py
# Typed contracts for prompt bundles

from dataclasses import dataclass
from langchain_core.messages import SystemMessage, HumanMessage


@dataclass(frozen=True)
class PromptBundle:
    #
    # Immutable bundle containing system and human messages for LLM invocation.
    #
    # Args:
    #     system_message: The system message defining LLM behavior and rules
    #     human_message: The human message containing context, question, and instructions
    #     rag_significant: Whether authoritative RAG context is present and significant
    #     rag_mode: Operating mode - "authoritative" or "fallback"
    #
    system_message: SystemMessage
    human_message: HumanMessage
    rag_significant: bool
    rag_mode: str
    
    def __post_init__(self):
        """Validate rag_mode values"""
        if self.rag_mode not in ("authoritative", "fallback"):
            raise ValueError(f"Invalid rag_mode: {self.rag_mode}. Must be 'authoritative' or 'fallback'")


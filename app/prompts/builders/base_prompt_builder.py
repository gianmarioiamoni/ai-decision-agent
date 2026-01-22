# app/prompts/builders/base_prompt_builder.py
# Base class for all prompt builders

class BasePromptBuilder:
    #
    # Base class for prompt builders.
    #
    # Provides common utilities for determining RAG significance and mode.
    # All prompt builders should inherit from this class.
    #
    
    # Minimum character length for RAG context to be considered significant
    RAG_SIGNIFICANT_THRESHOLD = 50
    
    @classmethod
    def is_rag_significant(cls, rag_context: str) -> bool:
        #
        # Determine if RAG context is significant enough to use authoritative mode.
        #
        # Args:
        #     rag_context: The RAG context string
        #
        # Returns:
        #     True if context exists and exceeds threshold, False otherwise
        #
        
        return bool(rag_context and len(rag_context) >= cls.RAG_SIGNIFICANT_THRESHOLD)
    
    @classmethod
    def determine_rag_mode(cls, rag_context: str) -> str:
        #
        # Determine the RAG mode based on context significance.
        #
        # Args:
        #     rag_context: The RAG context string
        #
        # Returns:
        #     "authoritative" if context is significant, "fallback" otherwise
        #
        
        return "authoritative" if cls.is_rag_significant(rag_context) else "fallback"


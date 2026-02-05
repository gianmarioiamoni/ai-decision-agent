# app/graph/nodes/planner_streaming.py
#
# Streaming version of planner node for real-time output generation.
#

from typing import Generator, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from app.prompts.builders import PlannerPromptBuilder


def planner_node_stream(
    question: str,
    context_docs: list
) -> Generator[str, None, None]:
    #
    # Stream planner output token-by-token.
    #
    # Args:
    #     question: User's question to analyze
    #     context_docs: Context documents for grounded planning
    #
    # Yields:
    #     Accumulated plan text chunks
    #
    
    # Validate input
    if not question:
        raise ValueError("Planner requires a valid question")
    
    # Build prompt using PlannerPromptBuilder
    bundle = PlannerPromptBuilder.build(
        question=question,
        context_docs=context_docs,
    )
    
    # Debug logging
    print("\n" + "="*60)
    print("🗺️  PLANNER PHASE (STREAMING)")
    print("="*60)
    print(f"📝 Question: {question[:100]}...")
    if bundle.rag_significant:
        print(f"✅ Context-Grounded Mode: Planning with organizational constraints")
    else:
        print(f"⚪ Generic Mode: Domain-agnostic planning")
    print("="*60 + "\n")
    
    # Initialize LLM with streaming enabled
    llm = ChatOpenAI(
        temperature=0.2,
        model="gpt-4o-mini",
        streaming=True  # Enable token-by-token streaming
    )
    
    # Create output parser
    output_parser = StrOutputParser()
    
    # Create LCEL chain
    chain = (
        llm | output_parser
    )
    
    # Stream tokens
    accumulated = ""
    for chunk in chain.stream([
        bundle.system_message,
        bundle.human_message,
    ]):
        accumulated += chunk
        yield accumulated


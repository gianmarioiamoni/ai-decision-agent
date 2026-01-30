# app/graph/nodes/analyzer_independent_streaming.py
#
# Independent streaming analyzer node (NO plan dependency).
#
# This analyzer operates INDEPENDENTLY from the planner, enabling parallel execution.
# It evaluates the question based solely on:
# - The question itself
# - Authoritative RAG context (user-uploaded documents)
# - Historical decisions (supportive context)
#
# Benefits:
# - 50% latency reduction (parallel LLM calls)
# - No confirmation bias (analyzer doesn't rubber-stamp the plan)
# - True cognitive separation (planner ≠ decision evaluator)
#

from typing import Generator
import re
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from app.prompts.builders import AnalyzerIndependentPromptBuilder
from app.prompts.historical_context_formatter import format_historical_context


def analyzer_independent_stream(
    question: str,
    rag_context: str,
    retrieved_docs: list,
    historical_evidence: list | None = None,
) -> Generator[str, None, None]:
    #
    # Stream independent analyzer output token-by-token.
    #
    # This function generates analysis WITHOUT depending on a plan,
    # enabling true parallel execution with the planner.
    #
    # Args:
    #     question: User's question
    #     rag_context: RAG context string (authoritative)
    #     retrieved_docs: Retrieved document metadata (supportive)
    #
    # Yields:
    #     Accumulated analysis text chunks
    #
    
    # Validate input
    if not question:
        raise ValueError("Analyzer requires a valid question")
    
    # Debug logging
    print("\n" + "="*60)
    print("🔍 ANALYZER INDEPENDENT PHASE (STREAMING)")
    print("="*60)
    print(f"📝 Question: {question[:100]}...")
    
    if rag_context:
        num_chunks = len(re.findall(r"\[CHUNK \d+\]", rag_context))
        print(f"✅ RAG Context Available: {len(rag_context)} chars, {num_chunks} chunks")
        print(f"📋 First 300 chars of context:")
        print(f"   {rag_context[:300].replace(chr(10), ' ')}...")
    else:
        print("❌ NO RAG Context - Using general reasoning only")
    
    historical_context = format_historical_context(
        historical_evidence or [],
    )

    if historical_context:
        print(f"✅ Historical Context Available: {len(historical_context)} chars")
        print(f"📋 First 300 chars of historical context:")
        print(f"   {historical_context[:300].replace(chr(10), ' ')}...")
    else:
        print("❌ NO Historical Context - Using general reasoning only")

    # Build prompt using Independent PromptBuilder (NO plan!)
    bundle = AnalyzerIndependentPromptBuilder.build(
        question=question,
        rag_context=rag_context,
        retrieved_docs=retrieved_docs,
        historical_context=historical_context,
    )
    
    print(f"\n🎯 RAG Mode: {bundle.rag_mode}")
    print(f"📤 System Prompt (first 400 chars):")
    print(f"   {bundle.system_message.content[:400]}...")
    
    print(f"\n📤 Human Prompt (first 400 chars):")
    print(f"   {bundle.human_message.content[:400]}...")
    print("="*60 + "\n")
    
    # Initialize LLM with streaming enabled
    llm = ChatOpenAI(
        temperature=0.3,
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


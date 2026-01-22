# app/graph/nodes/decision.py
# Decision node with long-term memory - refactored with PromptBuilder pattern

from typing import Dict
import re
from langchain_openai import ChatOpenAI
from app.graph.state import DecisionState
from app.graph.memory import init_chroma_vectorstore, retrieve_similar_decisions, save_decision
from app.prompts.builders import DecisionPromptBuilder

# Constants for confidence adjustment
SIMILARITY_THRESHOLD = 0.75  # Minimum similarity to consider historical decision
CONFIDENCE_BONUS = 0.10      # Increment confidence if similar decisions found (0.0 to 1.0)

# Initialize Chroma vectorstore (persistent)
chroma_store = init_chroma_vectorstore()


def decision_node(state: DecisionState) -> Dict:
    # Decision node using PromptBuilder pattern.
    #
    # Responsibilities:
    # - Validate input
    # - Retrieve similar past decisions
    # - Build prompt using DecisionPromptBuilder
    # - Invoke LLM
    # - Parse decision and confidence
    # - Adjust confidence based on historical decisions
    # - Save decision to long-term memory
    # - Return decision with metadata
    #

    # Validate required inputs
    question = state.get("question")
    analysis = state.get("analysis")
    rag_context = state.get("rag_context", "")
    
    if not question:
        raise ValueError("Decision node requires a valid question in state")
    if not analysis:
        raise ValueError("Decision node requires an analysis to make a decision")
    
    # -----------------------------
    # Retrieve similar decisions from long-term memory (Chroma)
    # -----------------------------
    similar_decisions = retrieve_similar_decisions(question, chroma_store, top_k=3)
    
    # 🔍 RAG DEBUG - Before prompt building
    print("\n" + "="*60)
    print("🔍 RAG DEBUG - DECISION PHASE (Before LLM)")
    print("="*60)
    print(f"📝 Question: {question[:100]}...")
    
    if rag_context:
        print(f"✅ RAG Context Available: {len(rag_context)} chars")
        print(f"📋 Context will be sent to LLM as AUTHORITATIVE")
    else:
        print("❌ NO RAG Context - Decision based on analysis only")
    
    if similar_decisions:
        print(f"📚 Historical Decisions: {len(similar_decisions)} similar past decisions")
    
    # 🆕 Build prompt using DecisionPromptBuilder (pure, deterministic)
    bundle = DecisionPromptBuilder.build(
        question=question,
        analysis=analysis,
        rag_context=rag_context,
        similar_decisions=similar_decisions,
    )
    
    print(f"\n🎯 RAG Mode: {bundle.rag_mode}")
    print(f"📤 System Prompt (first 600 chars):")
    print(f"   {bundle.system_message.content[:600]}...")
    
    print(f"\n📤 Human Prompt (first 400 chars):")
    print(f"   {bundle.human_message.content[:400]}...")
    print("="*60 + "\n")
    
    # Initialize LLM
    llm = ChatOpenAI(
        temperature=0.1,
        model="gpt-4o-mini"
    )
    
    # Invoke LLM
    response = llm.invoke([
        bundle.system_message,
        bundle.human_message,
    ])
    
    content = response.content.strip()
    
    # -----------------------------
    # Parse LLM response
    # -----------------------------
    decision_text = ""
    confidence_value = None
    context_factors = "No specific organizational context influenced this decision."
    
    # Regex to extract Decision, Confidence, and Contextual Factors
    decision_match = re.search(r'Decision[:\s]+(.+?)(?=Confidence:|$)', content, re.IGNORECASE | re.DOTALL)
    if decision_match:
        decision_text = decision_match.group(1).strip()
    
    confidence_match = re.search(r'Confidence[:\s]+([\d.]+)', content, re.IGNORECASE)
    if confidence_match:
        confidence_value = float(confidence_match.group(1))
    
    factors_match = re.search(r'Contextual Factors Influencing This Decision[:\s]*(.+)', content, re.IGNORECASE | re.DOTALL)
    if factors_match:
        context_factors = factors_match.group(1).strip()
    
    # Fallback defaults
    if not decision_text:
        decision_text = content
    if confidence_value is None:
        confidence_value = 0.75  # Default confidence 0.75 (float)
    
    # -----------------------------
    # Adjust confidence based on retrieved similar decisions
    # -----------------------------
    for sim in similar_decisions:
        if sim["similarity"] >= SIMILARITY_THRESHOLD:
            confidence_value = min(confidence_value + CONFIDENCE_BONUS, 1.0)  # Max 1.0
    
    # -----------------------------
    # Save decision to long-term memory
    # -----------------------------
    decision_id = save_decision(state=state, vectordb=chroma_store)
    
    # -----------------------------
    # Prepare messages for graph
    # -----------------------------
    messages = [
        {
            "role": "assistant",
            "content": f"Decision:\n{decision_text}\nConfidence: {confidence_value:.2f}\n\nContextual Factors:\n{context_factors}"
        }
    ]
    
    if similar_decisions:
        messages.append({
            "role": "system",
            "content": f"Retrieved {len(similar_decisions)} similar past decisions from memory."
        })
    
    if rag_context:
        messages.append({
            "role": "system",
            "content": f"Contextual documents from user considered in decision-making."
        })
    
    return {
        "decision": decision_text,
        "confidence": confidence_value,
        "rag_significant": bundle.rag_significant,
        "rag_mode": bundle.rag_mode,
        "messages": messages,
        "similar_decisions": similar_decisions  # Pass for UI display
    }

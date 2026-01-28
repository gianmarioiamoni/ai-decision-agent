# app/graph/nodes/planner.py
# Planner node - refactored with PromptBuilder pattern

from typing import Dict
from langchain_openai import ChatOpenAI
from app.graph.state import DecisionState
from app.prompts.builders import PlannerPromptBuilder


def planner_node(state: DecisionState) -> Dict:
    # Planner node using PromptBuilder pattern.
    #
    # Responsibilities:
    # - Validate input
    # - Build prompt using PlannerPromptBuilder
    # - Invoke LLM
    # - Return plan
    #
    # Key Feature: Context-Grounded Planning
    # - If context docs exist → generates plan with specific organizational constraints
    # - If no context → generates generic domain-agnostic plan
    #
    # This showcases decision intelligence vs generic LLM.
    #
    
    # Validate required inputs
    question = state.get("question")
    if not question:
        raise ValueError("Planner node requires a valid question in state")
    
    # Get context docs (if user uploaded them)
    context_docs = state.get("context_docs", [])
    
    # 🆕 Build prompt using PlannerPromptBuilder (pure, deterministic)
    bundle = PlannerPromptBuilder.build(
        question=question,
        context_docs=context_docs,
    )
    
    # 🔍 Debug logging
    print("\n" + "="*60)
    print("🗺️  PLANNER PHASE")
    print("="*60)
    print(f"📝 Question: {question[:100]}...")
    print("="*60 + "\n")
    if bundle.rag_significant:
        print(f"✅ Context-Grounded Mode: Planning with organizational constraints")
    else:
        print(f"⚪ Generic Mode: Domain-agnostic planning")
    print("="*60 + "\n")
    
    # Initialize LLM with low temperature for deterministic plans
    llm = ChatOpenAI(
        temperature=0.2,
        model="gpt-4o-mini"
    )
    
    # Invoke LLM
    response = llm.invoke([
        bundle.system_message,
        bundle.human_message,
    ])
    
    plan_text = response.content.strip()
    
    return {
        "plan": plan_text,
    }

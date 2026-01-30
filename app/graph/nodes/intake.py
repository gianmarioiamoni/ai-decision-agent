# app/graph/nodes/intake.py

from typing import Dict
from app.graph.state import DecisionState
from langchain_core.messages import HumanMessage

# Intake node
# Initializes the workflow by validating and normalizing
# the user input question and initializing conversation state
def intake_node(state: DecisionState) -> Dict:
    # Basic validation
    question = state.get("question")

    if not question or not question.strip():
        raise ValueError("Input question must be a non-empty string")

    # Normalize question
    normalized_question = question.strip()

    return {
        "question": normalized_question,
        "retrieved_docs": state.get("retrieved_docs", []),
        "plan": state.get("plan"),
        "analysis": state.get("analysis"),
        "decision": state.get("decision"),
        "confidence": state.get("confidence"),
        "messages": [
            HumanMessage(content=normalized_question)
        ],
        "attempts": 0,
        "decision_finalized": False, # Flag to indicate if the decision has been finalized
    }

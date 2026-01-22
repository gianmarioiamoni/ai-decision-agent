# app/graph/nodes/intake.py

from typing import Dict
from app.graph.state import DecisionState

# Intake node
# This node initializes the workflow by validating and normalizing
# the user input question and ensuring the state is correctly populated
def intake_node(state: DecisionState) -> Dict:
    # Basic validation: ensure a question is present
    question = state.get("question")

    if not question or not question.strip():
        raise ValueError("Input question must be a non-empty string")

    # Normalize the question
    normalized_question = question.strip()

    # Initialize mandatory fields if not already set
    return {
        "question": normalized_question,
        "retrieved_docs": state.get("retrieved_docs", []),
        "plan": state.get("plan"),
        "analysis": state.get("analysis"),
        "decision": state.get("decision"),
        "confidence": state.get("confidence"),
        # Add an initial message to the conversation history
        "messages": [
            {
                "role": "user",
                "content": normalized_question,
            }
        ],
        # Initialize attempts counter
        "attempts": 0,
        # Initialize decision finalization flag
        "decision_finalized": False,
    }

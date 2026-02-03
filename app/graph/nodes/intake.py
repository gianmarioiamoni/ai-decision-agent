# app/graph/nodes/intake.py

from app.graph.state import DecisionState
from langchain_core.messages import HumanMessage

def intake_node(state: DecisionState) -> DecisionState:
    # 
    # Intake node.
    # Validates and normalizes the user input.
    # This node MUST NOT create a new state.
    #
    # Args:
    #     state: DecisionState containing the user query
    #
    # Returns:
    #     DecisionState containing the normalized user query
    #

    if not state.user_query or not state.user_query.strip():
        raise ValueError("Input question must be a non-empty string")

    # Normalize question
    state.user_query = state.user_query.strip()

    # Initialize control flags (explicit, not implicit)
    state.needs_retry = False

    # NOTE:
    # - No messages here
    # - No attempts counter
    # - No decision flags
    # - No dict return
    state.messages.append(
        HumanMessage(content=state.user_query)
    )

    return state


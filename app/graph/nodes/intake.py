# app/graph/nodes/intake.py

from app.graph.state import DecisionState
from langchain_core.messages import HumanMessage

from infrastructure.logging.node_logger import log_node

from domain.context.context_hash import compute_context_hash


@log_node("intake")
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

    if not state["user_query"] or not state["user_query"].strip():
        raise ValueError("Input question must be a non-empty string")

    # Normalize question
    state["user_query"] = state["user_query"].strip()

    # Initialize control flags (explicit, not implicit)
    state.setdefault("retry_count", 0)
    state.setdefault("attempts", 0)
    state.setdefault("needs_retry", False)
    state.setdefault("used_fallback", False)
    state.setdefault("decision_finalized", False)
    state.setdefault("history_persisted", False)

    state["context_hash"] = compute_context_hash(
        state["user_query"],
        state.get("input_context_docs", []),
    )

    # NOTE:
    # - No messages here
    # - No attempts counter
    # - No decision flags
    # - No dict return
    state["messages"].append(
        HumanMessage(content=state["user_query"])
    )

    return state


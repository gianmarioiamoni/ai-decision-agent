# graph/router/policy_router.py

from typing import Literal
from app.graph.state import DecisionState
from app.graph.policy import DecisionPolicy

def policy_router(state: DecisionState) -> Literal[
    "retry",
    "continue",
    "fallback",
    "end",
]:
    return DecisionPolicy.evaluate(state)

# app/graph/router.py

from app.graph.state import DecisionState
from app.graph.policy import DecisionPolicy, DecisionOutcome

_policy = DecisionPolicy()


def decision_router(state: DecisionState) -> DecisionOutcome:
    return _policy.evaluate(state)

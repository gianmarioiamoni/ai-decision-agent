# app/graph/router/policy_router.py

from app.graph.state import DecisionState
from app.graph.policy import DecisionPolicy, DecisionOutcome


def policy_router(state: DecisionState) -> DecisionOutcome:
    policy = DecisionPolicy()

    outcome = policy.evaluate(state)
    assert outcome in {"retry", "continue", "fallback", "end"}

    return outcome


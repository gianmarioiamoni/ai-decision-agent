# tests/unit/test_decision_policy_routing.py

import pytest
from app.graph.policy import DecisionPolicy


@pytest.mark.parametrize(
    "state,expected",
    [
        # High confidence → continue
        (
            {
                "confidence_base": 0.9,
                "needs_retry": False,
                "attempts": 0,
                "decision_finalized": False,
                "analysis": "ok",
            },
            "continue",
        ),
        # Explicit retry
        (
            {
                "confidence_base": 0.9,
                "needs_retry": True,
                "attempts": 0,
                "decision_finalized": False,
                "analysis": "ok",
            },
            "retry",
        ),
        # Low confidence but attempts left
        (
            {
                "confidence_base": 0.4,
                "needs_retry": False,
                "attempts": 1,
                "decision_finalized": False,
                "analysis": "ok",
            },
            "retry",
        ),
        # Low confidence and no attempts left
        (
            {
                "confidence_base": 0.4,
                "needs_retry": False,
                "attempts": 3,
                "decision_finalized": False,
                "analysis": "ok",
            },
            "fallback",
        ),
        # Already finalized
        (
            {
                "confidence_base": 0.9,
                "needs_retry": False,
                "attempts": 0,
                "decision_finalized": True,
                "analysis": "ok",
            },
            "end",
        ),
    ],
)
def test_decision_policy_routing(state, expected):
    policy = DecisionPolicy(min_confidence=0.7, max_attempts=3)
    assert policy.evaluate(state) == expected

# tests/unit/test_decision_policy_effective_confidence.py

from app.graph.policy import DecisionPolicy


def test_effective_confidence_uses_base_confidence():
    policy = DecisionPolicy(min_confidence=0.7)

    state = {
        "confidence_base": 0.65,
        "needs_retry": False,
        "attempts": 0,
        "decision_finalized": False,
        "analysis": "analysis present",
    }

    assert policy.compute_effective_confidence(state) == 0.65

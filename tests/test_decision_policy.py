# tests/test_decision_policy.py

from app.graph.policy import DecisionPolicy

def base_state(**overrides):
    state = {
        "confidence_base": 0.8,
        "needs_retry": False,
        "attempts": 0,
        "decision_finalized": False,
        "analysis": "valid analysis"
    }
    state.update(overrides)
    return state


def test_retry_on_low_confidence():
    policy = DecisionPolicy(min_confidence=0.7, max_attempts=3)
    state = base_state(confidence_base=0.4)
    assert policy.evaluate(state) == "retry"


def test_fallback_after_max_attempts():
    policy = DecisionPolicy(min_confidence=0.7, max_attempts=2)
    state = base_state(confidence_base=0.4, attempts=2)
    assert policy.evaluate(state) == "fallback"


def test_continue_on_good_analysis():
    policy = DecisionPolicy()
    state = base_state()
    assert policy.evaluate(state) == "continue"


def test_end_when_finalized():
    policy = DecisionPolicy()
    state = base_state(decision_finalized=True)
    assert policy.evaluate(state) == "end"

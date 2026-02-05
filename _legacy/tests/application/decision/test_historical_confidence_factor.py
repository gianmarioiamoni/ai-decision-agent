# tests/application/decision/test_historical_confidence_factor.py

from app.application.decision.confidence_factor import historical_confidence_factor


def test_no_historical_evidence_returns_zero():
    assert historical_confidence_factor([]) == 0.0


def test_low_similarity_decisions_do_not_increase_confidence():
    evidence = [
        {"similarity": 0.40, "confidence": 0.9},
        {"similarity": 0.50, "confidence": 0.8},
    ]

    assert historical_confidence_factor(evidence) == 0.0


def test_single_high_similarity_decision_increases_confidence():
    evidence = [
        {"similarity": 0.85, "confidence": 0.9},
    ]

    value = historical_confidence_factor(evidence)

    assert 0.0 < value <= 0.15


def test_multiple_high_similarity_decisions_are_capped():
    evidence = [
        {"similarity": 0.90, "confidence": 0.9},
        {"similarity": 0.88, "confidence": 0.85},
        {"similarity": 0.92, "confidence": 0.95},
    ]

    value = historical_confidence_factor(evidence)

    assert value <= 0.25


def test_missing_confidence_is_handled_gracefully():
    evidence = [
        {"similarity": 0.90},
        {"similarity": 0.88, "confidence": None},
    ]

    value = historical_confidence_factor(evidence)

    assert value > 0.0

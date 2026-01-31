from datetime import datetime, timezone

import pytest

from domain.decision.decision_record import DecisionRecord
from domain.decision.decision_validation import validate_decision_record


def make_valid_record(**overrides) -> DecisionRecord:
    base = {
        "decision_id": "decision-1",
        "timestamp": datetime.now(timezone.utc),
        "question": "Should we adopt solution X?",
        "decision": "YES",
        "confidence": 0.9,
        "rationale": "Strong alignment with technical and business requirements",
        "key_factors": ["cost", "scalability"],
        "authoritative_context_refs": ["policy-1"],
        "historical_context_refs": [],
        "project_id": "project-1",
        "tags": ["architecture"]
    }

    base.update(overrides)
    return DecisionRecord(**base)


def test_valid_decision_record_passes_validation():
    record = make_valid_record()

    # Should not raise
    validate_decision_record(record)


def test_confidence_below_zero_raises_error():
    record = make_valid_record(confidence=-0.1)

    with pytest.raises(ValueError):
        validate_decision_record(record)


def test_confidence_above_one_raises_error():
    record = make_valid_record(confidence=1.1)

    with pytest.raises(ValueError):
        validate_decision_record(record)


def test_empty_question_raises_error():
    record = make_valid_record(question=" ")

    with pytest.raises(ValueError):
        validate_decision_record(record)


def test_empty_rationale_raises_error():
    record = make_valid_record(rationale="")

    with pytest.raises(ValueError):
        validate_decision_record(record)


def test_conditional_decision_without_key_factors_raises_error():
    record = make_valid_record(
        decision="CONDITIONAL",
        key_factors=[]
    )

    with pytest.raises(ValueError):
        validate_decision_record(record)


def test_conditional_decision_with_key_factors_passes_validation():
    record = make_valid_record(
        decision="CONDITIONAL",
        key_factors=["regulatory approval", "cost ceiling"]
    )

    validate_decision_record(record)

from datetime import datetime

import pytest

from app.application.decision.decision_state_mapper import (
    map_state_to_decision_record,
)
from domain.decision.decision_record import DecisionRecord


def make_valid_state(**overrides) -> dict:
    base_state = {
        "question": "Should we adopt solution X?",
        "decision": "YES",
        "confidence": 0.85,
        "analysis": "Detailed technical and business analysis.",
        "report_preview": "Final summarized rationale.",
        "retrieved_docs": [],
        "rag_context": None,
        "attempts": 1,
        "project_id": "project-1",
        "messages": [],
    }

    base_state.update(overrides)
    return base_state


def test_mapper_creates_decision_record_from_valid_state():
    state = make_valid_state()

    record = map_state_to_decision_record(state)

    assert isinstance(record, DecisionRecord)
    assert record.question == state["question"]
    assert record.decision == state["decision"]
    assert record.confidence == state["confidence"]
    assert record.project_id == state["project_id"]

    assert record.rationale == state["report_preview"]
    assert record.timestamp <= datetime.utcnow()


def test_mapper_uses_analysis_when_report_preview_missing():
    state = make_valid_state(report_preview=None)

    record = map_state_to_decision_record(state)

    assert record.rationale == state["analysis"]


def test_mapper_populates_key_factors():
    state = make_valid_state(attempts=2)

    record = map_state_to_decision_record(state)

    assert any("attempts_" in factor for factor in record.key_factors)


def test_mapper_raises_error_for_invalid_confidence():
    state = make_valid_state(confidence=1.5)

    with pytest.raises(ValueError):
        map_state_to_decision_record(state)


def test_mapper_handles_missing_optional_fields_gracefully():
    state = {
        "question": "Minimal valid question?",
        "decision": "NO",
        "confidence": 0.6,
        "analysis": "Negative analysis.",
        "messages": [],
    }

    record = map_state_to_decision_record(state)

    assert record.decision == "NO"
    assert record.key_factors
    assert record.project_id == "default"

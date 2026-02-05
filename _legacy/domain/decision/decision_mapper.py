# domain/decision/decision_mapper.py
from uuid import uuid4
from datetime import datetime, timezone

from domain.decision.decision_record import DecisionRecord
from domain.decision.decision_validation import validate_decision_record


def map_decision_result_to_record(decision_result) -> DecisionRecord:
    record = DecisionRecord(
        decision_id=str(uuid4()),
        timestamp=datetime.now(timezone.utc),

        question=decision_result.question,
        decision=decision_result.decision,
        confidence=decision_result.confidence,

        # 🔑 SOLO rationale sintetico
        justification=decision_result.justification,

        key_factors=decision_result.key_factors or [],

        project_id=decision_result.project_id,
        tags=decision_result.tags or [],

        # 🔑 complet report HTML
        report_html=decision_result.report_html,
    )

    validate_decision_record(record)
    return record


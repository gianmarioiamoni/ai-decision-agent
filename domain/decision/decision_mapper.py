from datetime import datetime
from uuid import uuid4

from domain.decision.decision_record import DecisionRecord
from domain.decision.decision_validation import validate_decision_record


def map_decision_result_to_record(decision_result) -> DecisionRecord:
    record = DecisionRecord(
        decision_id=str(uuid4()),
        timestamp=datetime.utcnow(),

        question=decision_result.question,

        decision=decision_result.final_decision,
        confidence=decision_result.confidence,

        rationale=decision_result.rationale,
        key_factors=decision_result.key_factors,

        authoritative_context_refs=decision_result.authoritative_context_ids,
        historical_context_refs=decision_result.historical_context_ids,

        project_id=decision_result.project_id,
        tags=decision_result.tags,
    )

    validate_decision_record(record)
    return record

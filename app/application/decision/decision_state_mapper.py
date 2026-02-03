from datetime import datetime, timezone
from uuid import uuid4

from domain.decision.decision_record import DecisionRecord
from domain.decision.decision_validation import validate_decision_record

from app.graph.state import DecisionState


def map_state_to_decision_record(state: DecisionState) -> DecisionRecord:
    # Maps a finalized Decision state to a DecisionRecord.
    # Must be called ONLY after decision + summarize phases.
    record = DecisionRecord(
        decision_id=str(uuid4()),
        question=state["user_query"],
        decision=state["decision"],
        confidence=state["confidence_final"],
        short_rationale="\n".join(state["justification"]), # memory contract
        key_factors=[],
        project_id=state["input_metadata"].get("project_id"),   # TODO: add project_id to input_metadata,
        tags=state["input_metadata"].get("tags", []),
        report_html=state["justification"] or "",
        timestamp=datetime.now(timezone.utc),
    )

    validate_decision_record(record)
    return record

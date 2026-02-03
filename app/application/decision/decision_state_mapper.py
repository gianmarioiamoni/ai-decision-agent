from datetime import datetime, timezone
from uuid import uuid4

from domain.decision.decision_record import DecisionRecord
from domain.decision.decision_validation import validate_decision_record

from app.graph.state import DecisionState


def map_state_to_decision_record(state: DecisionState) -> DecisionRecord:
    # Maps a finalized Decision state to a DecisionRecord.
    # Must be called ONLY after decision + summarize phases.
    
    # Get justification (could be string or list)
    justification = state.get("justification", "")
    if isinstance(justification, list):
        justification = "\n".join(justification)
    
    record = DecisionRecord(
        decision_id=str(uuid4()),
        question=state.get("user_query", ""),
        decision=state.get("decision", ""),
        confidence=state.get("confidence_final", 0.0),
        justification=justification,
        key_factors=[],
        project_id=None,  # No input_metadata in dict state
        tags=[],
        report_html=justification,
        timestamp=datetime.now(timezone.utc),
    )

    validate_decision_record(record)
    return record

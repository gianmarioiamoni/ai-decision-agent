from datetime import datetime, timezone
from uuid import uuid4

from domain.decision.decision_record import DecisionRecord
from domain.decision.decision_validation import validate_decision_record


def map_state_to_decision_record(state: dict) -> DecisionRecord:
    """
    Maps a finalized Decision state to a DecisionRecord.
    Must be called ONLY after decision + summarize phases.
    """

    record = DecisionRecord(
        decision_id=str(uuid4()),
        question=state["question"],
        decision=state["decision"],
        confidence=state["confidence"],
        short_rationale=state["short_rationale"],  # 🔑 obbligatorio
        key_factors=state.get("key_factors", []),
        project_id=state.get("project_id"),
        tags=state.get("tags", []),
        report_html=state.get("report_html", ""),
        timestamp=datetime.now(timezone.utc),
    )

    validate_decision_record(record)
    return record

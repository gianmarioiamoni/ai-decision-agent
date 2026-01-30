from domain.decision.decision_record import DecisionRecord

def validate_decision_record(record: DecisionRecord) -> None:
    if not 0.0 <= record.confidence <= 1.0:
        raise ValueError("Confidence must be between 0.0 and 1.0")

    if not record.question.strip():
        raise ValueError("Question cannot be empty")

    if not record.rationale.strip():
        raise ValueError("Rationale cannot be empty")

    if record.decision == "CONDITIONAL" and not record.key_factors:
        raise ValueError("Conditional decisions must specify key factors")

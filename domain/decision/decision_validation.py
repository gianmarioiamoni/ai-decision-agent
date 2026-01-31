from domain.decision.decision_record import DecisionRecord


def validate_decision_record(record: DecisionRecord) -> None:
    # Confidence range
    if not 0.0 <= record.confidence <= 1.0:
        raise ValueError("Confidence must be between 0.0 and 1.0")

    # Question is mandatory
    if not record.question.strip():
        raise ValueError("Question cannot be empty")

    # Decision outcome is mandatory
    if not record.decision.strip():
        raise ValueError("Decision cannot be empty")

    # 🔑 Short rationale is mandatory (memory contract)
    if not record.short_rationale.strip():
        raise ValueError("Short rationale cannot be empty")

    # Key factors required only for conditional decisions
    if record.decision.upper() == "CONDITIONAL" and not record.key_factors:
        raise ValueError("Conditional decisions must specify key factors")


# domain/decision/decision_result.py
class DecisionResult:
    question: str
    final_decision: str
    confidence: float
    rationale: str
    key_factors: list[str]

    authoritative_context_ids: list[str]
    historical_context_ids: list[str]

    project_id: str
    tags: list[str]

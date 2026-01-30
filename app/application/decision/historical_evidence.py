from dataclasses import dataclass


@dataclass(frozen=True)
class HistoricalDecisionEvidence:
    decision_id: str
    decision: str
    confidence: float
    rationale: str
    similarity_score: float

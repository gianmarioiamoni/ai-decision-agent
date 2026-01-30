from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal


DecisionOutcome = Literal["YES", "NO", "CONDITIONAL"]


@dataclass(frozen=True)
class DecisionRecord:
    # Identity
    decision_id: str
    timestamp: datetime

    # Core question
    question: str

    # Outcome
    decision: DecisionOutcome
    confidence: float  # [0.0 - 1.0]

    # Rationale
    rationale: str
    key_factors: List[str]

    # Context references (by id / source, not raw text)
    authoritative_context_refs: List[str]
    historical_context_refs: List[str]

    # Classification
    project_id: str
    tags: List[str]

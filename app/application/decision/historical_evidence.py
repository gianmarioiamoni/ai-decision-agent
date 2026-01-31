from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class HistoricalDecisionEvidence:
    decision: str
    confidence: float
    rationale: str
    similarity_score: float
    timestamp: Optional[datetime] = None

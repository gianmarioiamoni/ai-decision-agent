# domain/decision/historical_decision_evidence.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class HistoricalDecisionEvidence:
    # Value object representing a past decision used as historical evidence.

    decision: str
    confidence: float
    similarity_score: float
    rationale: Optional[str] = None
    timestamp: Optional[datetime] = None

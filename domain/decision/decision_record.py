# domain/decision/decision_record.py

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass(frozen=True)
class DecisionRecord:
    decision_id: str
    question: str
    decision: str
    confidence: float

    # 🔑 NUOVO: rationale sintetico per memoria
    short_rationale: str

    # opzionali / contesto
    key_factors: List[str]
    project_id: Optional[str]
    tags: List[str]

    # output UI
    report_html: str

    timestamp: datetime


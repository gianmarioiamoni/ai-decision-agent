# domain/metrics/confidence_drift.py

from typing import List

def confidence_drift(
    history: List[float],
    current: float,
    window: int = 5
) -> float:
    if not history:
        return 0.0

    recent = history[-window:]
    avg = sum(recent) / len(recent)
    return abs(current - avg)

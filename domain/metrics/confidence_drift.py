# domain/metrics/confidence_drift.py
#
# Domain metric: confidence drift
# Measures deviation of current confidence from historical average
#

from typing import List


def compute_confidence_drift(
    history: List[float],
    current: float,
) -> float:
    #
    # No history → no drift
    #
    if not history:
        return 0.0

    average = sum(history) / len(history)
    return current - average

# domain/metrics/confidence.py

from typing import Iterable
from app.prompts.constants import SIMILARITY_THRESHOLD

def compute_similarity_confidence_bonus(
    similarities: Iterable[float],
    confidences: Iterable[float],
    similarity_threshold: float = SIMILARITY_THRESHOLD,
    confidence_bonus: float = 0.1,
    max_bonus: float = 0.2,
) -> float:
    bonus = 0.0

    for similarity, confidence in zip(similarities, confidences):
        if similarity >= similarity_threshold and confidence > 0:
            bonus += confidence_bonus

    return min(bonus, max_bonus)

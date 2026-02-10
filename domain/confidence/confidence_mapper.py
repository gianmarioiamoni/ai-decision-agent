# app/domain/confidence/confidence_mapper.py

from typing import Literal

ConfidenceLabel = Literal["High", "Medium", "Low"]


def map_confidence_label(confidence: float) -> ConfidenceLabel:
    if confidence >= 0.80:
        return "High"
    if confidence >= 0.55:
        return "Medium"
    return "Low"

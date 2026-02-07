from typing import List
from domain.decision.historical_decision_evidence import HistoricalDecisionEvidence


def format_historical_context(
    evidences: List[HistoricalDecisionEvidence],
) -> str:
    if not evidences:
        return ""

    lines = [
        "Previous similar decisions (supportive evidence only):"
    ]

    for e in evidences:
        lines.append(
            f"- Decision: {e.decision} "
            f"(confidence={e.confidence:.2f}, "
            f"similarity={e.similarity_score:.2f})"
        )

    return "\n".join(lines)

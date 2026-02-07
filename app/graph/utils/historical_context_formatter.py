# app/graph/utils/historical_context_formatter.py

from typing import Iterable
from domain.history.history_repository import HistoricalDecision


def format_historical_context(
    historical_decisions: Iterable[HistoricalDecision] | None,
) -> str:
    #
    # Domain-level formatter for historical decisions.
    # Used inside LangGraph nodes (analyzer).
    #
    if not historical_decisions:
        return ""

    lines = [
        "Previous similar decisions (historical context):"
    ]

    for item in historical_decisions:
        lines.append(
            f"- Decision: {item.decision} "
            f"(confidence={item.confidence:.2f})"
        )

    return "\n".join(lines)

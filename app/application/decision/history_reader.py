# app/application/decision/history_reader.py

# This function:
# - read all decision history from Chroma
# - does not do similarity search (serve to the UI, not to the LLM)
# - returns a list of HistoricalDecisionEvidence
# - is safe if the DB is empty
# - does not introduce coupling with the UI

from typing import List

from infrastructure.memory.chroma_client import get_chroma_collection
from app.application.decision.historical_evidence import (
    HistoricalDecisionEvidence,
)


def load_decision_history(limit: int = 20) -> List[HistoricalDecisionEvidence]:
    #
    # Load global historical decision history for UI display.
    #
    # Args:
    #     limit: Maximum number of decisions to return
    #
    # Returns:
    #     List of HistoricalDecisionEvidence
    #

    collection = get_chroma_collection()

    try:
        results = collection.get(
            include=["documents", "metadatas"],
        )
    except Exception as e:
        print(f"[HISTORY] ⚠️ Failed to load history: {e}")
        return []

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    history: List[HistoricalDecisionEvidence] = []

    for doc, meta in zip(documents, metadatas):
        try:
            history.append(
                HistoricalDecisionEvidence(
                    decision=meta.get("decision", ""),
                    confidence=float(meta.get("confidence", 0.0)),
                    similarity_score=0.0,  # not applicable for global history
                    rationale=doc,
                    timestamp=meta.get("timestamp"),
                )
            )
        except Exception as e:
            print(f"[HISTORY] ⚠️ Skipping corrupted record: {e}")
            continue

    # Best-effort ordering: newest first if timestamp exists
    history.sort(
        key=lambda h: h.timestamp or "",
        reverse=True,
    )

    return history[:limit]
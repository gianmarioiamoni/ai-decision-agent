# app/application/decision/history_reader.py

# This function:
# - read all decision history from Chroma
# - does not do similarity search (serve to the UI, not to the LLM)
# - returns a list of HistoricalDecisionEvidence
# - is safe if the DB is empty
# - does not introduce coupling with the UI

from datetime import datetime
from typing import List

from infrastructure.memory.chroma_client import get_chroma_collection
from app.application.decision.historical_evidence import HistoricalDecisionEvidence


def load_decision_history(limit: int = 20) -> List[HistoricalDecisionEvidence]:
    collection = get_chroma_collection()

    try:
        result = collection.get(
            limit=limit,
            include=["documents", "metadatas"]
        )
    except Exception as e:
        print(f"[HISTORY] ❌ Failed to load history: {e}")
        return []

    history: List[HistoricalDecisionEvidence] = []

    for meta in result.get("metadatas", []):
        try:
            raw_ts = meta.get("timestamp")

            timestamp = (
                datetime.fromisoformat(raw_ts)
                if isinstance(raw_ts, str)
                else None
            )

            history.append(
                HistoricalDecisionEvidence(
                    decision_id=meta.get("decision_id", ""),
                    decision=meta.get("decision", ""),
                    confidence=float(meta.get("confidence", 0.0)),
                    similarity_score=0.0,
                    timestamp=timestamp,
                )
            )

        except Exception as e:
            print(f"[HISTORY] ⚠️ Skipping corrupted record: {e}")

    print(f"[HISTORY] ✅ Loaded {len(history)} historical decisions")
    return history

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection

from domain.decision.decision_record import DecisionRecord


class HistoricalDecisionWriter:
    def __init__(self, collection: "Collection") -> None:
        self._collection = collection

    def persist(self, record: DecisionRecord) -> None:
        document = self._build_document(record)
        metadata = self._build_metadata(record)

        self._collection.add(
            ids=[record.decision_id],
            documents=[document],
            metadatas=[metadata],
        )

    def _build_document(self, record: DecisionRecord) -> str:
        return record.short_rationale.strip()

    def _build_metadata(self, record: DecisionRecord) -> dict:
        metadata = {
            "decision_id": record.decision_id,
            "decision": record.decision,
            "confidence": float(record.confidence),
            "timestamp": record.timestamp.isoformat(),
            "context_type": "historical",
        }

        return metadata

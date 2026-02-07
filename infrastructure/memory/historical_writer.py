# infrastructure/memory/historical_writer.py

from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection


class HistoricalWriter:
    #
    # Low-level persistence adapter for historical decisions.
    # Accepts normalized primitives, not domain objects.
    #
    def __init__(self, collection: "Collection") -> None:
        self._collection = collection

    def write(
        self,
        *,
        context_hash: str,
        decision: str,
        confidence: float,
        justification: str | None = None,
        project_id: str | None = None,
        tags: list[str] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        #
        # Persist a historical decision snapshot.
        #
        document = self._build_document(justification)
        metadata = self._build_metadata(
            context_hash=context_hash,
            decision=decision,
            confidence=confidence,
            project_id=project_id,
            tags=tags,
            timestamp=timestamp,
        )

        self._collection.add(
            ids=[context_hash],
            documents=[document],
            metadatas=[metadata],
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_document(self, justification: str | None) -> str:
        return (justification or "").strip()

    def _build_metadata(
        self,
        *,
        context_hash: str,
        decision: str,
        confidence: float,
        project_id: str | None,
        tags: list[str] | None,
        timestamp: datetime | None,
    ) -> dict:
        metadata = {
            "context_hash": context_hash,
            "decision": decision,
            "confidence": float(confidence),
            "timestamp": (
                timestamp.isoformat()
                if timestamp is not None
                else datetime.utcnow().isoformat()
            ),
            "context_type": "historical",
        }

        if project_id:
            metadata["project_id"] = project_id

        if tags:
            metadata["tags"] = ",".join(tags)

        return metadata


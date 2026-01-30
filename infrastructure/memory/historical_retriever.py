from typing import TYPE_CHECKING, List

from app.application.decision.historical_evidence import (
    HistoricalDecisionEvidence,
)

if TYPE_CHECKING:
    from chromadb.api.models.Collection import Collection


class HistoricalDecisionRetriever:
    def __init__(self, collection: "Collection") -> None:
        self._collection = collection

    def retrieve(
        self,
        query: str,
        k: int = 3,
    ) -> List[HistoricalDecisionEvidence]:

        results = self._collection.query(
            query_texts=[query],
            n_results=k,
        )

        evidences: List[HistoricalDecisionEvidence] = []

        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]
            document = results["documents"][0][i]
            distance = results["distances"][0][i]

            evidences.append(
                HistoricalDecisionEvidence(
                    decision_id=metadata.get("decision_id"),
                    decision=metadata.get("decision"),
                    confidence=metadata.get("confidence"),
                    rationale=document,
                    similarity_score=1.0 - distance,  # cosine similarity
                )
            )

        return evidences

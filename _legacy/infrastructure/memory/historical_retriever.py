# infrastructure/memory/historical_retriever.py
#
# Infrastructure-level historical decision retriever.
# - NO dependency on app.*
# - NO business logic
# - Returns plain dicts (DTOs)
#

from typing import List, Dict, Any


class HistoricalDecisionRetriever:
    def __init__(self, collection):
        self._collection = collection

    def retrieve(
        self,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        #
        # Raw retrieval from vector store.
        # Interpretation and business logic are OUTSIDE this layer.
        #
        results = self._collection.query(
            query_texts=[query],
            n_results=limit,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        evidences: List[Dict[str, Any]] = []

        for doc, meta, distance in zip(documents, metadatas, distances):
            evidences.append(
                {
                    "decision": meta.get("decision"),
                    "confidence": meta.get("confidence"),
                    # Convert distance → similarity
                    "similarity_score": 1.0 - float(distance),
                }
            )

        return evidences

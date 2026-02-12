# domain/history/history_repository.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
import hashlib
from datetime import datetime, timezone

from app.prompts.constants import SIMILARITY_THRESHOLD, HISTORICAL_TOP_K


# =========================
# Domain model
# =========================

@dataclass(frozen=True)
class HistoricalDecision:
    context_hash: str
    decision: str
    confidence: float
    similarity: float | None = None
    timestamp: datetime | None = None


# =========================
# Repository port (interface)
# =========================

class HistoryRepository(ABC):
    # Lookup historical decisions for a given context
    @abstractmethod
    def lookup(self, context_hash: str) -> List[HistoricalDecision]:
        pass
    # Persist decision only if not already present (idempotent)
    @abstractmethod
    def persist_if_absent(
        self,
        context_hash: str,
        user_query: str,
        decision: str,
        confidence: float
    ) -> None:
        pass

    @abstractmethod
    def lookup_similar(
        self,
        query_text: str,
        top_k: int = HISTORICAL_TOP_K,
    ) -> List[HistoricalDecision]:
        pass


# =========================
# In-memory implementation (tests / local dev)
# =========================

class InMemoryHistoryRepository(HistoryRepository):
    def __init__(self) -> None:
        self._storage: dict[str, List[HistoricalDecision]] = {}

    def lookup(self, context_hash: str) -> List[HistoricalDecision]:
        return list(self._storage.get(context_hash, []))

    def persist_if_absent(
        self,
        context_hash: str,
        decision: str,
        confidence: float
    ) -> None:
        existing = self._storage.get(context_hash, [])

        for item in existing:
            if item.decision == decision:
                return

        record = HistoricalDecision(
            context_hash=context_hash,
            decision=decision,
            confidence=confidence
        )

        self._storage.setdefault(context_hash, []).append(record)



# =========================
# ChromaDB implementation (infrastructure)
# =========================

class ChromaHistoryRepository(HistoryRepository):
    def __init__(self, collection) -> None:
        # collection is an already-initialized ChromaDB collection
        self._collection = collection

    def lookup(self, context_hash: str) -> List[HistoricalDecision]:
        results = self._collection.get(
            where={"context_hash": {"$eq": context_hash}}
        )

        metadatas = results.get("metadatas", [])

        history: List[HistoricalDecision] = []

        for metadata in metadatas:
            history.append(
                HistoricalDecision(
                    context_hash=metadata["context_hash"],
                    decision=metadata["decision"],
                    confidence=float(metadata["confidence"])
                )
            )

        return history

    def persist_if_absent(
        self,
        context_hash: str,
        user_query: str,
        decision: str,
        confidence: float
    ) -> None:
        existing = self._collection.get(
            where={
                "$and": [
                    {"context_hash": context_hash},
                    {"decision": decision}
                ]
            }
        )

        if existing.get("ids"):
            return
        
        stable_hash = hashlib.sha256(decision.encode()).hexdigest()
        record_id = f"{context_hash}:{hash(stable_hash)}"
        
        self._collection.add(
            ids=[record_id],
            documents=[user_query],
            metadatas=[{
                "context_hash": context_hash,
                "decision": decision,
                "confidence": confidence,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        )    
        print("COLLECTION COUNT AFTER INSERT (ChromaHistoryRepository):", self._collection.count())

    
    def lookup_similar(
        self,
        query_text: str,
        top_k: int = HISTORICAL_TOP_K,
    ) -> List[HistoricalDecision]:

        results = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
        )

        print("COLLECTION COUNT:", self._collection.count())
        print("RAW QUERY RESULTS:", results)

        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        history = []

        for metadata, distance in zip(metadatas, distances):
            similarity = 1 - distance  # cosine distance → similarity

            if similarity < SIMILARITY_THRESHOLD:
                continue
                
            timestamp = None
            if metadata.get("timestamp"):
                timestamp = datetime.fromisoformat(metadata["timestamp"])
                
            history.append(
                HistoricalDecision(
                    context_hash=metadata["context_hash"],
                    decision=metadata["decision"],
                    confidence=float(metadata["confidence"]),
                    similarity=float(similarity),
                    timestamp=timestamp
                )
            )

        # sort for similarity DESC
        history.sort(key=lambda x: x.similarity or 0, reverse=True)

        return history

    

# domain/history/history_repository.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


# =========================
# Domain model
# =========================

@dataclass(frozen=True)
class HistoricalDecision:
    context_hash: str
    decision: str
    confidence: float


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
        decision: str,
        confidence: float
    ) -> None:
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

        self._collection.add(
            documents=[decision],
            metadatas=[{
                "context_hash": context_hash,
                "decision": decision,
                "confidence": confidence
            }]
        )

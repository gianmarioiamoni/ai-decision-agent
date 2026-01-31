# tests/integration/test_historical_memory.py

from datetime import datetime, timezone

from domain.decision.decision_record import DecisionRecord
from infrastructure.memory.historical_writer import HistoricalDecisionWriter
from infrastructure.memory.historical_retriever import HistoricalDecisionRetriever
from app.application.decision.history_reader import load_decision_history

from infrastructure.memory.chroma_client import get_chroma_collection


def test_historical_memory_full_flow():
    """
    Integration test:
    - persist a decision
    - retrieve via similarity
    - retrieve via history reader
    """

    # ------------------------------------------------------------------
    # SETUP
    # ------------------------------------------------------------------
    collection = get_chroma_collection()

    # 🔥 CLEAN SLATE
    collection.delete(where={"context_type": "historical"})

    writer = HistoricalDecisionWriter(collection)
    retriever = HistoricalDecisionRetriever(collection)

    record = DecisionRecord(
        decision_id="test-decision-001",
        question="Should we adopt Python?",
        decision="Do not adopt Python",
        confidence=0.72,
        rationale="- Lack of performance guarantees\n- No org context",
        key_factors=["performance", "missing context"],
        project_id="test-project",
        tags=["tech", "language"],
        timestamp=datetime.now(timezone.utc),
    )

    # ------------------------------------------------------------------
    # ACT 1: PERSIST
    # ------------------------------------------------------------------
    writer.persist(record)

    # ------------------------------------------------------------------
    # ACT 2: SIMILARITY RETRIEVAL (LLM PATH)
    # ------------------------------------------------------------------
    evidences = retriever.retrieve(
        query="Should we adopt Python?",
        k=3,
    )

    # ------------------------------------------------------------------
    # ASSERT: SIMILARITY
    # ------------------------------------------------------------------
    assert len(evidences) >= 1

    ev = evidences[0]

    assert ev.decision_id == record.decision_id
    assert ev.decision == record.decision
    assert ev.confidence == record.confidence

    # 🔑 rationale MUST be concise, not report
    assert "AI Decision Session Report" not in ev.rationale
    assert len(ev.rationale) < 500

    assert 0.0 <= ev.similarity_score <= 1.0

    # ------------------------------------------------------------------
    # ACT 3: HISTORY READER (UI PATH)
    # ------------------------------------------------------------------
    history = load_decision_history(limit=10)

    # ------------------------------------------------------------------
    # ASSERT: HISTORY
    # ------------------------------------------------------------------
    assert len(history) >= 1

    h = history[0]

    assert h.decision_id == record.decision_id
    assert h.decision == record.decision
    assert h.confidence == record.confidence
    assert h.timestamp is not None

    # rationale must be the same stored one
    assert "AI Decision Session Report" not in h.rationale

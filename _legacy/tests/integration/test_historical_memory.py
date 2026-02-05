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
    - persist a decision into historical memory
    - retrieve via similarity (LLM path)
    - retrieve via history reader (UI path)
    """

    # ------------------------------------------------------------------
    # SETUP
    # ------------------------------------------------------------------
    collection = get_chroma_collection()

    # 🔥 CLEAN SLATE (only historical memory)
    collection.delete(where={"context_type": "historical"})

    writer = HistoricalDecisionWriter(collection)
    retriever = HistoricalDecisionRetriever(collection)

    record = DecisionRecord(
        decision_id="test-decision-001",
        question="Should we adopt Python?",
        decision="Do not adopt Python",
        confidence=0.72,

        # 🔑 concise memory-safe rationale
        short_rationale="Lack of authoritative context and performance concerns",

        key_factors=["performance", "missing context"],
        project_id="test-project",
        tags=["tech", "language"],

        # 🔑 required by domain, but irrelevant for memory
        report_html="<html><body>Test report</body></html>",

        timestamp=datetime.now(timezone.utc),
    )

    # ------------------------------------------------------------------
    # ACT 1: PERSIST (writer)
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

    # 🔑 must NOT contain full report
    assert "AI Decision Session Report" not in ev.rationale
    assert "Test report" not in ev.rationale

    # rationale must be concise, memory-oriented
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

    # 🔑 history rationale must NOT contain report
    assert "AI Decision Session Report" not in h.rationale
    assert "Test report" not in h.rationale


from datetime import datetime

from domain.decision.decision_record import DecisionRecord
from infrastructure.memory.historical_writer import HistoricalDecisionWriter


class FakeChromaCollection:
    def __init__(self):
        self.add_called = False
        self.ids = None
        self.documents = None
        self.metadatas = None

    def add(self, ids, documents, metadatas):
        self.add_called = True
        self.ids = ids
        self.documents = documents
        self.metadatas = metadatas


def make_decision_record() -> DecisionRecord:
    return DecisionRecord(
        decision_id="decision-123",
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        question="Should we adopt solution X?",
        decision="YES",
        confidence=0.9,
        rationale="Strong alignment with requirements",
        key_factors=["cost", "scalability"],
        authoritative_context_refs=["policy-1"],
        historical_context_refs=[],
        project_id="project-1",
        tags=["architecture"],
    )


def test_historical_writer_persists_decision_record():
    collection = FakeChromaCollection()
    writer = HistoricalDecisionWriter(collection)

    record = make_decision_record()

    writer.persist(record)

    # Assert collection.add was called
    assert collection.add_called is True

    # Assert IDs
    assert collection.ids == ["decision-123"]

    # Assert document content
    document = collection.documents[0]
    assert "Should we adopt solution X?" in document
    assert "YES" in document
    assert "Strong alignment with requirements" in document
    assert "cost" in document
    assert "scalability" in document

    # Assert metadata
    metadata = collection.metadatas[0]
    assert metadata["decision"] == "YES"
    assert metadata["confidence"] == 0.9
    assert metadata["project_id"] == "project-1"
    assert metadata["tags"] == ["architecture"]
    assert metadata["context_type"] == "historical"
    assert metadata["timestamp"] == "2024-01-01T12:00:00"

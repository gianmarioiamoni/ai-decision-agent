# tests/rag/test_rag_on_off.py
#
# Automated tests for RAG on/off decision logic.
#
# These tests verify that:
# - RAG is disabled when no embeddings are present
# - RAG is enabled after embedding documents
# - Clear removes embeddings and disables RAG
# - Decision logic relies ONLY on vectorstore state
#
# IMPORTANT:
# - No external API calls
# - No OpenAI dependency
# - Uses fake embeddings for deterministic behavior

from langchain_core.embeddings import Embeddings
from app.rag.vectorstore_manager import VectorstoreManager


# ------------------------------------------------------------------
# FAKE EMBEDDINGS (NO OPENAI, NO HTTP)
# ------------------------------------------------------------------

class FakeEmbeddings(Embeddings):
    #
    # Deterministic fake embeddings for testing.
    # Vector dimensionality is arbitrary but consistent.
    #
    def embed_documents(self, texts):
        return [[0.0] * 10 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 10


# ------------------------------------------------------------------
# TEST UTILITIES
# ------------------------------------------------------------------

def make_vsm() -> VectorstoreManager:
    #
    # Create a VectorstoreManager instance with fake embeddings.
    # Each test gets its own isolated manager instance.
    #
    return VectorstoreManager(embedding_function=FakeEmbeddings())


def rag_should_be_enabled(vsm: VectorstoreManager) -> bool:
    #
    # Decision logic under test:
    # RAG is enabled ONLY if embeddings exist.
    #
    return vsm.count() > 0


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------

def test_rag_disabled_when_empty():
    vsm = make_vsm()

    vsm.clear()

    assert vsm.count() == 0
    assert vsm.has_documents() is False
    assert rag_should_be_enabled(vsm) is False


def test_rag_enabled_after_embedding():
    vsm = make_vsm()
    vsm.clear()

    docs = [
        "This is a test document about enterprise decision systems.",
        "Second document with strategic insights.",
    ]

    added = vsm.add_documents(docs)

    assert added > 0
    assert vsm.count() > 0
    assert vsm.has_documents() is True
    assert rag_should_be_enabled(vsm) is True


def test_clear_disables_rag():
    vsm = make_vsm()

    docs = ["Temporary document for clearing test"]
    vsm.add_documents(docs)

    assert vsm.count() > 0
    assert rag_should_be_enabled(vsm) is True

    vsm.clear()

    assert vsm.count() == 0
    assert vsm.has_documents() is False
    assert rag_should_be_enabled(vsm) is False


def test_rag_decision_logic():
    vsm = make_vsm()
    vsm.clear()

    assert rag_should_be_enabled(vsm) is False

    vsm.add_documents(["Persistent enterprise knowledge base"])

    assert rag_should_be_enabled(vsm) is True

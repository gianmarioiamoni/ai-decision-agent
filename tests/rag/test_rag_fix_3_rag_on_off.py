# tests/rag/test_rag_fix_3_rag_on_off.py

import pytest
from app.rag.bootstrap import bootstrap_rag

# ------------------------------------------------------------------
# FAKES
# ------------------------------------------------------------------

class FakeVectorstoreManager:
    def __init__(self):
        self._count = 0
        self.initialized = False

    def get_vectorstore(self):
        self.initialized = True
        return self

    def count(self):
        return self._count

    def has_documents(self):
        return self._count > 0

    def add_documents(self, documents, **kwargs):
        self._count += len(documents)
        return len(documents)

    def clear(self):
        self._count = 0


class FakeFileManager:
    def refresh_state(self):
        return []


# ------------------------------------------------------------------
# FIXTURES
# ------------------------------------------------------------------

@pytest.fixture
def fake_env(monkeypatch):
    fake_vsm = FakeVectorstoreManager()
    fake_fm = FakeFileManager()

    monkeypatch.setattr(
        "app.rag.bootstrap.get_vectorstore_manager",
        lambda: fake_vsm,
    )

    monkeypatch.setattr(
        "app.rag.bootstrap.get_file_manager",
        lambda: fake_fm,
    )

    return fake_vsm


# ------------------------------------------------------------------
# TESTS — FIX 3
# ------------------------------------------------------------------

def test_bootstrap_does_not_enable_rag(fake_env):
    """
    bootstrap_rag must NOT create embeddings.
    RAG must remain disabled.
    """
    bootstrap_rag()

    assert fake_env.initialized is True
    assert fake_env.count() == 0
    assert fake_env.has_documents() is False


def test_rag_disabled_when_no_embeddings(fake_env):
    """
    RAG is disabled when vectorstore is empty.
    """
    assert fake_env.count() == 0
    assert fake_env.has_documents() is False


def test_rag_enabled_after_embedding(fake_env):
    """
    Adding documents enables RAG.
    """
    fake_env.add_documents(["doc1", "doc2"])

    assert fake_env.count() == 2
    assert fake_env.has_documents() is True


def test_clear_disables_rag(fake_env):
    """
    Clearing embeddings disables RAG.
    """
    fake_env.add_documents(["doc1"])
    assert fake_env.has_documents() is True

    fake_env.clear()

    assert fake_env.count() == 0
    assert fake_env.has_documents() is False


def test_bootstrap_does_not_change_existing_rag_state(fake_env):
    """
    bootstrap_rag must NOT alter RAG state.
    """
    fake_env.add_documents(["doc1"])
    assert fake_env.has_documents() is True

    bootstrap_rag()

    assert fake_env.count() == 1
    assert fake_env.has_documents() is True

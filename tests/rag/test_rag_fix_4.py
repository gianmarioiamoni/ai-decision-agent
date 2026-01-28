from app.rag.vectorstore_manager import get_vectorstore_manager, _reset_vectorstore_manager
from app.rag.bootstrap import bootstrap_rag
from langchain_core.embeddings import Embeddings


class FakeEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [[0.0] * 5 for _ in texts]

    def embed_query(self, text):
        return [0.0] * 5


def test_bootstrap_does_not_create_embeddings():
    _reset_vectorstore_manager()
    vsm = get_vectorstore_manager(
        embedding_function=FakeEmbeddings()
    )
    vsm.clear()

    assert vsm.count() == 0

    bootstrap_rag()

    assert vsm.count() == 0


def test_bootstrap_does_not_change_existing_embeddings(tmp_path):
    _reset_vectorstore_manager()

    vsm = get_vectorstore_manager(
        embedding_function=FakeEmbeddings(),
        chroma_dir=tmp_path / "chroma_test",
    )

    vsm.clear()
    vsm.add_documents(["test document"])

    before = vsm.count()
    assert before > 0

    bootstrap_rag()

    after = vsm.count()
    assert after == before

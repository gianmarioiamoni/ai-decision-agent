# app/rag/vectorstore_manager.py
#
# Manages persistent ChromaDB vectorstore with HF Hub synchronization.
# Responsible ONLY for:
# - chunking
# - embeddings
# - vectorstore persistence
#
# File ownership and registry are handled by FileManager.

from pathlib import Path
from typing import List, Dict

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.hf_persistence import get_hf_persistence


# ------------------------------------------------------------------
# SINGLETON
# ------------------------------------------------------------------

_vectorstore_instance = None


class VectorstoreManager:
    """
    VectorstoreManager

    Responsibilities:
    - Persistent ChromaDB storage
    - Text chunking
    - Embedding generation
    - Optional HF Hub sync

    Does NOT:
    - Know about files
    - Manage registry
    - Access filesystem documents
    """

    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.chroma_dir = self.project_root / "chroma_db"
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

        self.hf_persistence = get_hf_persistence()
        self._embeddings = OpenAIEmbeddings()
        self._vectorstore: Chroma | None = None

        print("[VECTORSTORE] 📦 Initialized")
        print(f"[VECTORSTORE] 📁 Chroma dir: {self.chroma_dir}")

    # ------------------------------------------------------------------
    # INIT / LOAD
    # ------------------------------------------------------------------

    def get_vectorstore(self) -> Chroma:
        if self._vectorstore is None:
            self._initialize_vectorstore()
        return self._vectorstore

    def _initialize_vectorstore(self):
        print("\n[VECTORSTORE] 🔧 Initializing vectorstore")

        if self.hf_persistence and self.hf_persistence.api:
            print("[VECTORSTORE] ☁️ Attempting HF Hub download...")
            self.hf_persistence.download_vectorstore()

        self._vectorstore = Chroma(
            persist_directory=str(self.chroma_dir),
            embedding_function=self._embeddings,
        )

        self._warmup()
        print("[VECTORSTORE] ✅ Vectorstore ready")

    def _warmup(self):
        try:
            self._vectorstore.similarity_search(" ", k=1)
            print("[VECTORSTORE] 🔥 Warmup completed")
        except Exception as e:
            print(f"[VECTORSTORE] ⚠️ Warmup skipped: {e}")

    # ------------------------------------------------------------------
    # ADD DOCUMENTS
    # ------------------------------------------------------------------

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict] | None = None,
        sync_to_hub: bool = False,
    ) -> int:
        if not documents:
            return 0

        vectorstore = self.get_vectorstore()

        chunks: List[str] = []
        chunk_metadatas: List[Dict] = []

        for i, doc in enumerate(documents):
            doc_chunks = self._chunk_text(doc)
            chunks.extend(doc_chunks)

            base_meta = metadatas[i] if metadatas else {}
            for idx in range(len(doc_chunks)):
                chunk_metadatas.append({
                    **base_meta,
                    "chunk_id": idx + 1,
                    "total_chunks": len(doc_chunks),
                    "doc_index": i,
                })

        print(f"[VECTORSTORE] 💾 Adding {len(chunks)} chunks")
        vectorstore.add_texts(chunks, metadatas=chunk_metadatas)

        if sync_to_hub:
            self._sync_to_hub()
        else:
            print("[VECTORSTORE] ℹ️ HF sync skipped")

        return len(chunks)

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        return self.get_vectorstore().similarity_search(query, k=k)

    # ------------------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------------------

    def clear(self):
        print("[VECTORSTORE] 🗑️ Clearing vectorstore")

        import shutil

        self._vectorstore = None

        if self.chroma_dir.exists():
            shutil.rmtree(self.chroma_dir)

        self.chroma_dir.mkdir(parents=True, exist_ok=True)

        if self.hf_persistence and self.hf_persistence.api:
            self.hf_persistence.clear_remote_vectorstore()

        print("[VECTORSTORE] ✅ Cleared")

    # ------------------------------------------------------------------
    # HF SYNC
    # ------------------------------------------------------------------

    def _sync_to_hub(self):
        if not self.hf_persistence or not self.hf_persistence.api:
            return

        print("[VECTORSTORE] ☁️ Syncing to HF Hub")
        self.hf_persistence.upload_vectorstore()

    # ------------------------------------------------------------------
    # CHUNKING
    # ------------------------------------------------------------------

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 300,
        overlap: int = 100,
    ) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            overlap=overlap,
            separators=["\n\n", "\n", " ", "", ".", "?", "!", ":", ";", ","],
        )
        chunks = splitter.split_text(text)
        print(f"[VECTORSTORE] ✂️ {len(chunks)} chunks created")
        return chunks


# ------------------------------------------------------------------
# SINGLETON ACCESS
# ------------------------------------------------------------------

def get_vectorstore_manager() -> VectorstoreManager:
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = VectorstoreManager()
    return _vectorstore_instance


def reset_vectorstore_singleton():
    global _vectorstore_instance
    _vectorstore_instance = None
    print("[VECTORSTORE] 🔄 Singleton reset")

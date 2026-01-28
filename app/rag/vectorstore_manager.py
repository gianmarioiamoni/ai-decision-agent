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

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.rag.hf_persistence import get_hf_persistence
from app.config.settings import EMBEDDING_MODEL_NAME

# ------------------------------------------------------------------
# SINGLETON
# ------------------------------------------------------------------

_vectorstore_instance = None


_VECTORSTORE_MANAGER = None


def get_vectorstore_manager(embedding_function=None, chroma_dir: Path | None = None):
    global _VECTORSTORE_MANAGER

    if _VECTORSTORE_MANAGER is None:
        _VECTORSTORE_MANAGER = VectorstoreManager(
            embedding_function=embedding_function,
            chroma_dir=chroma_dir
        )

    return _VECTORSTORE_MANAGER


def _reset_vectorstore_manager():
    global _VECTORSTORE_MANAGER
    _VECTORSTORE_MANAGER = None

class VectorstoreManager:
    #
    # Responsibilities:
    # - Persistent ChromaDB storage
    # - Text chunking
    # - Embedding generation
    # - Optional HF Hub sync
    #
    # Does NOT:
    # - Know about files
    # - Manage registry

    def __init__(self, embedding_function = None, chroma_dir: Path | None = None):
        self.embedding_function = embedding_function
        self._vectorstore = None
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.chroma_dir = (
            chroma_dir
            if chroma_dir is not None
            else self.project_root / "chroma_db"
        )
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

        self.hf_persistence = get_hf_persistence()
        self._embeddings = (
            self.embedding_function
            if embedding_function is not None
            else OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        )

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

        # IMPORTANT:
        # - initialized ONCE per process
        # - NEVER destroyed or recreated at runtime
        self._vectorstore = Chroma(
            persist_directory=str(self.chroma_dir),
            embedding_function=self.embedding_function,
        )

        print("[VECTORSTORE] ✅ Vectorstore ready")

    

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
                chunk_metadatas.append(
                    {
                        **base_meta,
                        "chunk_id": idx + 1,
                        "total_chunks": len(doc_chunks),
                        "doc_index": i,
                    }
                )

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
    # CLEAR (FIX 1 – SAFE, NO RESTART)
    # ------------------------------------------------------------------

    def clear(self) -> None:
        print("[VECTORSTORE] 🧹 Clearing embeddings (safe)")

        vectorstore = self.get_vectorstore()
        collection = vectorstore._collection
        count = collection.count()

        if count == 0:
            print("[VECTORSTORE] ℹ️ No embeddings to delete")
            return
        
        # delete by ids
        items = collection.get(include=[])
        all_ids = items.get("ids", [])
        if not all_ids:
            print("[VECTORSTORE] ℹ️ No embeddings to delete")
            return
        
        collection.delete(ids=all_ids)
        print(f"[VECTORSTORE] 🗑️ Deleted {count} embeddings")

        print("[VECTORSTORE] ✅ Vectorstore cleared")

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
        chunk_overlap: int = 100,
    ) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", "", ".", "?", "!", ":", ";", ","],
        )

        chunks = splitter.split_text(text)
        print(f"[VECTORSTORE] ✂️ {len(chunks)} chunks created")
        return chunks

    # ------------------------------------------------------------------
    # CHECK DOCUMENTS PRESENCE
    # ------------------------------------------------------------------

    def has_documents(self) -> bool:
            collection = self.get_vectorstore()._collection
            return collection.count() > 0


    def count(self) -> int:
        try:
            collection = self.get_vectorstore()._collection
            return collection.count()
        except Exception:
            return 0


#

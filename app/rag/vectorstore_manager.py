# app/rag/vectorstore_manager.py
#
# Manages persistent ChromaDB vectorstore with HF Hub synchronization.
# Responsible ONLY for:
# - chunking
# - embeddings
# - vectorstore persistence
#
# File ownership and registry are handled by FileManager.

import os
from pathlib import Path
from typing import List, Dict, Callable

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
        
        # Restore indexed files from metadata
        try:
            collection = self._vectorstore._collection
            metadatas = collection.get(include=["metadatas"]).get("metadatas", [])

            for meta in metadatas:
                if meta and "filename" in meta:
                    self._indexed_files.add(meta["filename"])

            print(f"[VECTORSTORE] 🔁 Restored {len(self._indexed_files)} indexed files")
        except Exception as e:
            print(f"[VECTORSTORE] ⚠️ Could not restore indexed files: {e}")

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

        # Drop in-memory reference to avoid data loss
        self._vectorstore = None

        # Remove local Chroma DB directory
        if self.chroma_dir.exists():
            shutil.rmtree(self.chroma_dir)
            print(f"[VECTORSTORE] 🗑️ Removed local dir: {self.chroma_dir}")

        # Recreate empty directory
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

        # reset indexed files tracking
        self._indexed_files.clear()

        print("[VECTORSTORE] ✅ Local vectorstore cleared")
        print("[VECTORSTORE] ℹ️ Remote HF Hub snapshot untouched")

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
    # ENSURE INDEXED FILES
    # ------------------------------------------------------------------

    def ensure_indexed_files(
        self, 
        files: List[Dict], 
        read_file_fn: Callable[[str], str]
    ) -> int:
        #
        # Ensure all files are indexed in the vectorstore.
        #
        # Args:
        #     files: List of files from FileManager
        #     read_file_fn: Function to read the file content
        #
        # Returns:
        #     int: Number of newly indexed files
        #
        # Implements:
        # - Stateless w.r.t. files
        # - Relies on Chroma persistence for idempotency
        # - Safe to call multiple times (idempotent)
        # - FileManager is the source of truth
        #

        if not files:
            print("[VECTORSTORE] ℹ️ No files to index")
            return 0

        vectorstore = self.get_vectorstore()
        added_chunks = 0
        for file in files:
            filename = file.get("name")
            path = file.get("path")

            try:
                content = read_file_fn(path)
                if not content.strip():
                    print(f"[VECTORSTORE] ⚠️ Empty file skipped: {filename}")
                    continue  

                chunks = self._chunk_text(content)
                metadatas = [
                {
                    "filename": filename,
                    "source": path,
                    "chunk_id": idx + 1,
                    "total_chunks": len(chunks),
                } for idx in range(len(chunks))]

                vectorstore.add_texts(chunks, metadatas=metadatas)
                added_chunks += len(chunks)

                print(f"[VECTORSTORE] ✅ Indexed {filename} ({len(chunks)} chunks)")
            except Exception as e:
                print(f"[VECTORSTORE] ❌ Failed indexing {filename}: {e}")
                continue

        print(f"[VECTORSTORE] 🎉 Indexing complete: {added_chunks} chunks added")
        return added_chunks


# ------------------------------------------------------------------
# SINGLETON ACCESS
# ------------------------------------------------------------------

def get_vectorstore_manager() -> VectorstoreManager:
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = VectorstoreManager()
    return _vectorstore_instance

def ensure_indexed_files(self, files, read_file_fn):
    vectorstore = self.get_vectorstore()

    newly_indexed = 0

    for file in files:
        filename = file.get("name")
        path = file.get("path")

        if not filename or not path:
            continue

        # 🔒 Already indexed → skip
        if filename in self._indexed_files:
            continue

        print(f"[VECTORSTORE] 📄 Indexing missing file: {filename}")

        try:
            content = read_file_fn(path)
        except Exception as e:
            print(f"[VECTORSTORE] ⚠️ Failed reading {filename}: {e}")
            continue

        self.add_documents(
            documents=[content],
            metadatas=[{
                "filename": filename,
                "source": path,
            }],
            sync_to_hub=False,
        )

        self._indexed_files.add(filename)
        newly_indexed += 1

    print(f"[VECTORSTORE] ✅ Bootstrap complete: {newly_indexed} file(s) indexed")
 


def reset_vectorstore_singleton():
    global _vectorstore_instance
    _vectorstore_instance = None
    print("[VECTORSTORE] 🔄 Singleton reset")

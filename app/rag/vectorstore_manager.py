# app/rag/vectorstore_manager.py
#
# Manages persistent ChromaDB vectorstore with HF Hub synchronization.
# Ensures RAG context is preserved across HF Space restarts.

import os
from pathlib import Path
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.rag.hf_persistence import get_hf_persistence


# Singleton instance
_vectorstore_instance = None


class VectorstoreManager:
    # Manages persistent ChromaDB vectorstore with HF Hub sync.
    # 
    # Features:
    # - Persistent local storage in chroma_db/
    # - Automatic sync with HF Hub
    # - Lazy loading (creates on first use)
    # - Incremental updates when new files are added
    
    def __init__(self):
        # Initialize VectorstoreManager.
        
        # Paths
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self.chroma_dir = self.project_root / "chroma_db"
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        # HF persistence
        self.hf_persistence = get_hf_persistence()
        
        # Vectorstore (lazy init)
        self._vectorstore = None
        self._embeddings = OpenAIEmbeddings()
        
        # Track indexed files
        self._indexed_files = set()
        
        print(f"[VECTORSTORE] 📦 Initialized")
        print(f"[VECTORSTORE] 📁 Local dir: {self.chroma_dir}")
    
    def get_vectorstore(self) -> Chroma:
        # Get or create the persistent vectorstore.
        # 
        # Returns:
        #     Chroma vectorstore instance
        
        if self._vectorstore is None:
            self._initialize_vectorstore()
        return self._vectorstore
    
    def _initialize_vectorstore(self):
        # Initialize vectorstore with HF Hub sync.
        
        print(f"\n[VECTORSTORE] 🔧 Initializing...")
        
        # Try to download from HF Hub if available
        if self.hf_persistence and self.hf_persistence.api:
            print(f"[VECTORSTORE] 📥 Attempting to download from HF Hub...")
            if self.hf_persistence.download_vectorstore():
                print(f"[VECTORSTORE] ✅ Loaded from HF Hub")
            else:
                print(f"[VECTORSTORE] 📭 No existing vectorstore on HF Hub, starting fresh")
        
        # Create/load persistent vectorstore
        self._vectorstore = Chroma(
            persist_directory=str(self.chroma_dir),
            embedding_function=self._embeddings
        )
        
        print(f"[VECTORSTORE] ✅ Vectorstore ready")
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict] = None
    ) -> int:
        # Add documents to vectorstore with chunking.
        # 
        # Args:
        #     documents: List of document texts
        #     metadatas: Optional list of metadata dicts
        # 
        # Returns:
        #     Number of chunks added
        
        if not documents:
            return 0
        
        vectorstore = self.get_vectorstore()
        
        # Chunk documents
        all_chunks = []
        all_metadatas = []
        
        for doc_idx, doc in enumerate(documents):
            chunks = self._chunk_text(doc)
            all_chunks.extend(chunks)
            
            # Create metadata for each chunk
            base_metadata = metadatas[doc_idx] if metadatas else {}
            for chunk_idx in range(len(chunks)):
                chunk_metadata = {
                    **base_metadata,
                    'chunk_id': chunk_idx + 1,
                    'total_chunks': len(chunks),
                    'doc_index': doc_idx
                }
                all_metadatas.append(chunk_metadata)
        
        # Add to vectorstore
        print(f"[VECTORSTORE] 💾 Adding {len(all_chunks)} chunks to Chroma...")
        vectorstore.add_texts(texts=all_chunks, metadatas=all_metadatas)
        
        print(f"[VECTORSTORE] ✅ Added {len(all_chunks)} chunks from {len(documents)} documents")
        
        # Force persist to disk before syncing to HF Hub
        print(f"[VECTORSTORE] 💾 Persisting to disk...")
        try:
            # ChromaDB in newer versions doesn't have explicit persist()
            # The data is automatically persisted when using persist_directory
            pass
        except Exception as e:
            print(f"[VECTORSTORE] ⚠️ Persist warning: {e}")
        
        # Sync to HF Hub
        self._sync_to_hub()
        
        return len(all_chunks)
    
    def clear(self):
        # Clear all documents from vectorstore.
        
        print(f"[VECTORSTORE] 🗑️ Clearing vectorstore...")
        
        # Close existing vectorstore connection
        if self._vectorstore is not None:
            try:
                # ChromaDB doesn't have explicit close, just reset reference
                self._vectorstore = None
            except Exception as e:
                print(f"[VECTORSTORE] ⚠️ Error closing vectorstore: {e}")
        
        # Remove chroma_db directory completely
        import shutil
        if self.chroma_dir.exists():
            try:
                shutil.rmtree(self.chroma_dir)
                print(f"[VECTORSTORE] 🗑️ Removed directory: {self.chroma_dir}")
            except Exception as e:
                print(f"[VECTORSTORE] ⚠️ Error removing directory: {e}")
        
        # Recreate empty directory
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        print(f"[VECTORSTORE] 📁 Recreated empty directory: {self.chroma_dir}")
        
        # Reinitialize empty vectorstore
        self._vectorstore = Chroma(
            persist_directory=str(self.chroma_dir),
            embedding_function=self._embeddings
        )
        
        self._indexed_files.clear()
        
        # Clear on HF Hub
        if self.hf_persistence and self.hf_persistence.api:
            try:
                self.hf_persistence.clear_remote_vectorstore()
                print(f"[VECTORSTORE] ☁️ Cleared from HF Hub")
            except Exception as e:
                print(f"[VECTORSTORE] ⚠️ Error clearing HF Hub: {e}")
        
        print(f"[VECTORSTORE] ✅ Cleared")
    
    def similarity_search(
        self,
        query: str,
        k: int = 5
    ) -> List[Document]:
        # Search for similar documents.
        # 
        # Args:
        #     query: Search query
        #     k: Number of results to return
        # 
        # Returns:
        #     List of similar documents
        
        vectorstore = self.get_vectorstore()
        return vectorstore.similarity_search(query, k=k)
    
    def _sync_to_hub(self):
        # Sync vectorstore to HF Hub.
        
        if not self.hf_persistence:
            print(f"[VECTORSTORE] ⚠️ HF persistence not available")
            return
        
        if not self.hf_persistence.api:
            print(f"[VECTORSTORE] ⚠️ HF API not initialized")
            return
        
        try:
            print(f"[VECTORSTORE] ☁️ Starting sync to HF Hub...")
            success = self.hf_persistence.upload_vectorstore()
            if success:
                print(f"[VECTORSTORE] ✅ Successfully synced to HF Hub")
            else:
                print(f"[VECTORSTORE] ⚠️ Sync to HF Hub returned False")
        except Exception as e:
            print(f"[VECTORSTORE] ❌ Exception during HF Hub sync: {e}")
            import traceback
            traceback.print_exc()
    
    def _chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 100) -> List[str]:
        # Split text into overlapping chunks.
        # 
        # Args:
        #     text: Text to chunk
        #     chunk_size: Size of each chunk
        #     overlap: Overlap between chunks
        # 
        # Returns:
        #     List of text chunks
        
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start = end - overlap
        return chunks


def get_vectorstore_manager() -> VectorstoreManager:
    # Get singleton VectorstoreManager instance.
    # 
    # Returns:
    #     VectorstoreManager instance
    
    global _vectorstore_instance
    if _vectorstore_instance is None:
        _vectorstore_instance = VectorstoreManager()
    return _vectorstore_instance


def reset_vectorstore_singleton():
    # Reset the singleton instance (used after clear operations).
    # This ensures a fresh start when reinitializing the vectorstore.
    
    global _vectorstore_instance
    if _vectorstore_instance is not None:
        print("[VECTORSTORE] 🔄 Resetting singleton instance")
        _vectorstore_instance = None


# app/rag/hf_persistence.py
#
# Hugging Face Hub Persistence Layer for RAG Documents and ChromaDB
#
# This module handles persistent storage of:
# 1. RAG document registry (rag_documents.json)
# 2. ChromaDB vectorstore (chroma_db.tar.gz)
#
# Storage location: HF Space repository itself (Git-backed)

import os
import json
import tarfile
import tempfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from huggingface_hub import HfApi, hf_hub_download, upload_file


class HFPersistence:
    # Persistent storage manager for HF Spaces using Hub API
    
    # Configuration - reads from environment or uses defaults
    HF_USERNAME = os.getenv("SPACE_AUTHOR_NAME", "gianmarioiamoni67")
    HF_REPO = os.getenv("SPACE_REPO_NAME", "ai-decision-agent")
    HF_TOKEN = os.getenv("HF_TOKEN")  # Automatically available in HF Spaces
    
    # File names in HF Hub repository
    REGISTRY_FILE = "rag_documents.json"
    CHROMA_ARCHIVE = "chroma_db.tar.gz"
    
    # Local paths
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    CHROMA_DIR = PROJECT_ROOT / "chroma_db"  # RAG vectorstore (not chroma_memory)
    
    def __init__(self):
        try:
            self.api = HfApi()
            print(f"[HF_PERSISTENCE] ✅ Initialized for {self.HF_USERNAME}/{self.HF_REPO}")
            print(f"[HF_PERSISTENCE] Token available: {bool(self.HF_TOKEN)}")
        except Exception as e:
            print(f"[HF_PERSISTENCE] ⚠️ Error initializing HfApi: {e}")
            self.api = None
    
    # ============ RAG DOCUMENT REGISTRY ============
    
    def load_registry(self) -> List[Dict]:
        # Load RAG document registry from HF Hub
        #
        # Returns:
        #     List of document metadata dictionaries
        
        print(f"\n{'='*60}")
        print(f"📥 Loading RAG document registry from HF Hub...")
        
        # Check if HfApi is available
        if not self.api:
            print("⚠️ HfApi not initialized, returning empty registry")
            print(f"{'='*60}\n")
            return []
        
        try:
            # Force download from server, not cache
            file_path = hf_hub_download(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.REGISTRY_FILE,
                repo_type="space",
                token=self.HF_TOKEN,
                force_download=True,  # Bypass local cache
            )
            
            with open(file_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
                print(f"✅ Loaded RAG document registry: {len(registry)} files")
                print(f"{'='*60}\n")
            return registry
            
        except Exception as e:
            # If file doesn't exist or other error, return empty list
            if "404" in str(e) or "Entry Not Found" in str(e):
                print("📭 No existing RAG document registry found, starting fresh")
            else:
                print(f"⚠️ Could not load RAG registry: {e}")
            print(f"{'='*60}\n")
            return []
    
    def save_registry(self, registry: List[Dict]) -> bool:
        # Save RAG document registry to HF Hub
        #
        # Args:
        #     registry: List of document metadata dictionaries
        #
        # Returns:
        #     True if successful, False otherwise
        
        print(f"\n{'='*60}")
        print(f"☁️ Saving RAG document registry to HF Hub...")
        
        try:
            # Save to temp file first
            temp_file = os.path.join(tempfile.gettempdir(), self.REGISTRY_FILE)
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(registry, f, ensure_ascii=False, indent=2)
            
            # Upload to HF Hub
            upload_file(
                path_or_fileobj=temp_file,
                path_in_repo=self.REGISTRY_FILE,
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                repo_type="space",
                token=self.HF_TOKEN,
                commit_message=f"Update RAG registry: {len(registry)} documents",
            )
            
            print(f"✅ Saved RAG document registry: {len(registry)} files")
            print(f"{'='*60}\n")
            
            # Cleanup temp file
            os.remove(temp_file)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save RAG registry to HF Hub: {e}")
            print(f"{'='*60}\n")
            return False
    
    def add_document(self, filename: str, source: str) -> bool:
        # Add a document to the registry
        #
        # Args:
        #     filename: Name of the document file
        #     source: Source path of the document
        #
        # Returns:
        #     True if successful, False otherwise
        
        registry = self.load_registry()
        
        # Check if already exists
        if any(doc["filename"] == filename for doc in registry):
            print(f"⚠️ Document {filename} already in registry")
            return True
        
        # Add new document
        registry.append({
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "source": source
        })
        
        return self.save_registry(registry)
    
    def clear_registry(self) -> bool:
        # Clear all documents from the registry
        #
        # Returns:
        #     True if successful, False otherwise
        
        return self.save_registry([])
    
    # ============ CHROMADB VECTORSTORE ============
    
    def _compress_chroma_dir(self, output_path: str) -> bool:
        # Compress chroma_db/ directory to .tar.gz
        #
        # Args:
        #     output_path: Path where to save the .tar.gz archive
        #
        # Returns:
        #     True if successful, False otherwise
        
        if not self.CHROMA_DIR.exists():
            print(f"⚠️ Chroma directory not found: {self.CHROMA_DIR}")
            return False
        
            try:
                with tarfile.open(output_path, "w:gz") as tar:
                    tar.add(str(self.CHROMA_DIR), arcname="chroma_db")
                
                size_mb = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Compressed chroma_db to {output_path} ({size_mb:.2f} MB)")
                return True
            except Exception as e:
                print(f"❌ Failed to compress chroma_db: {e}")
            return False
    
    def _extract_chroma_archive(self, archive_path: str) -> bool:
        # Extract chroma_db.tar.gz to local directory
        #
        # Args:
        #     archive_path: Path to the .tar.gz archive
        #
        # Returns:
        #     True if successful, False otherwise
        
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extractall(path=str(self.PROJECT_ROOT))
            
            print(f"✅ Extracted chroma_db from {archive_path}")
            return True
        except Exception as e:
            print(f"❌ Failed to extract chroma_db: {e}")
            return False
    
    def upload_vectorstore(self) -> bool:
        # Upload local chroma_db/ to HF Hub
        #
        # Returns:
        #     True if successful, False otherwise
        
        print(f"\n{'='*60}")
        print(f"☁️ Uploading vectorstore to HF Hub...")
        
        # Check if chroma_db exists locally
        if not self.CHROMA_DIR.exists():
            print(f"⚠️ No local chroma_db to upload")
            print(f"{'='*60}\n")
            return False
        
        # Create temporary archive
        temp_archive = os.path.join(tempfile.gettempdir(), self.CHROMA_ARCHIVE)
        
        try:
            # Compress
            if not self._compress_chroma_dir(temp_archive):
                return False
            
            # Upload to HF Hub
            upload_file(
                path_or_fileobj=temp_archive,
                path_in_repo=self.CHROMA_ARCHIVE,
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                repo_type="space",
                token=self.HF_TOKEN,
                commit_message="Update ChromaDB vectorstore",
            )
            
            size_mb = os.path.getsize(temp_archive) / (1024 * 1024)
            print(f"✅ Uploaded vectorstore to HF Hub ({size_mb:.2f} MB)")
            print(f"{'='*60}\n")
            
            # Cleanup temp file
            os.remove(temp_archive)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload vectorstore to HF Hub: {e}")
            print(f"{'='*60}\n")
            
            # Cleanup temp file if exists
            if os.path.exists(temp_archive):
                os.remove(temp_archive)
            
            return False
    
    def download_vectorstore(self) -> bool:
        # Download chroma_db/ from HF Hub
        #
        # Returns:
        #     True if successful, False otherwise
        
        print(f"\n{'='*60}")
        print(f"📥 Downloading vectorstore from HF Hub...")
        
        try:
            # Download archive
            archive_path = hf_hub_download(
                repo_id=f"{self.HF_USERNAME}/{self.HF_REPO}",
                filename=self.CHROMA_ARCHIVE,
                repo_type="space",
                token=self.HF_TOKEN,
                force_download=True,
            )
            
            # Extract to local directory
            success = self._extract_chroma_archive(archive_path)
            
            if success:
                print(f"✅ Downloaded and extracted vectorstore from HF Hub")
            
            print(f"{'='*60}\n")
            return success
            
        except Exception as e:
            if "404" in str(e) or "Entry Not Found" in str(e):
                print("📭 No existing vectorstore found on HF Hub, starting fresh")
            else:
                print(f"⚠️ Could not download vectorstore: {e}")
            print(f"{'='*60}\n")
            return False
    
    def sync_from_hub(self) -> bool:
        # Sync vectorstore from HF Hub (download)
        #
        # Returns:
        #     True if successful, False otherwise
        
        return self.download_vectorstore()
    
    def sync_to_hub(self) -> bool:
        # Sync vectorstore to HF Hub (upload)
        #
        # Returns:
        #     True if successful, False otherwise
        
        return self.upload_vectorstore()


# Singleton instance
_hf_persistence_instance: Optional[HFPersistence] = None

def get_hf_persistence() -> HFPersistence:
    # Get singleton HF persistence instance
    #
    # Returns:
    #     HFPersistence singleton instance
    
    global _hf_persistence_instance
    if _hf_persistence_instance is None:
        _hf_persistence_instance = HFPersistence()
    return _hf_persistence_instance


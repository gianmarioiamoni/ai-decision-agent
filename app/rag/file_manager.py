# app/rag/file_manager.py
# RAG File Manager - Enterprise-Grade State Management for Context Documents.

import os
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# HF persistence
try:
    from app.rag.hf_persistence import get_hf_persistence
    from app.rag.vectorstore_manager import get_vectorstore_manager
    HF_PERSISTENCE_AVAILABLE = True
except Exception as e:
    HF_PERSISTENCE_AVAILABLE = False
    print(f"[FILE_MANAGER] ⚠️ HF persistence not available: {e}")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAG_STORAGE_DIR = PROJECT_ROOT / "data" / "uploaded_rag"
RAG_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class FileManager:
    
    # Stateful file manager for RAG context documents.

    # Responsibilities:
    # - Maintain authoritative file state
    # - Persist files locally
    # - Sync registry to HF Hub
    # - Trigger vectorstore updates (delegated)

    def __init__(self, storage_dir: Path = RAG_STORAGE_DIR):
        self.storage_dir = storage_dir
        self._files: List[Dict[str, str]] = []

        self.hf_persistence = (
            get_hf_persistence() if HF_PERSISTENCE_AVAILABLE else None
        )

        print("[FILE_MANAGER] 🏗️ Initialized (lazy loading)")

    # ------------------------------------------------------------------
    # HF HUB REGISTRY
    # ------------------------------------------------------------------

    def _load_from_hf_hub(self):
        print("\n[FILE_MANAGER] 📥 Loading registry from HF Hub")

        if not self.hf_persistence:
            self._files = []
            return

        registry = self.hf_persistence.load_registry()
        self._files = [
            {
                "name": doc["filename"],
                "path": doc.get("source", ""),
                "size": 0,
                "size_kb": 0.0,
                "modified": doc.get("uploaded_at", "N/A"),
                "timestamp": 0,
            }
            for doc in registry or []
            if "filename" in doc
        ]

        print(f"[FILE_MANAGER] ✅ Loaded {len(self._files)} file(s)")

    # ------------------------------------------------------------------
    # STATE REFRESH
    # ------------------------------------------------------------------

    def refresh_state(self) -> List[Dict[str, str]]:
        print("\n[FILE_MANAGER] 🔄 refresh_state()")

        self._files = []

        if self.hf_persistence:
            self._load_from_hf_hub()
            return self._files

        # Local filesystem (dev)
        for file_path in self.storage_dir.iterdir():
            if file_path.is_file() and file_path.name != ".gitkeep":
                stat = file_path.stat()
                self._files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "timestamp": stat.st_mtime,
                })

        self._files.sort(key=lambda x: x["timestamp"], reverse=True)
        return self._files

    # ------------------------------------------------------------------
    # FILE UPLOAD
    # ------------------------------------------------------------------

    def save_uploaded_file(self, file_path: str) -> Dict[str, str]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        original_name = Path(file_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        base, ext = os.path.splitext(original_name)
        stored_name = f"{base}_{timestamp}{ext}"
        stored_path = self.storage_dir / stored_name

        shutil.copy2(file_path, stored_path)

        file_info = {
            "name": stored_name,
            "path": str(stored_path),
            "size": stored_path.stat().st_size,
            "size_kb": round(stored_path.stat().st_size / 1024, 2),
            "modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": datetime.now().timestamp(),
        }

        self._files.append(file_info)

        # Registry only (HF-safe)
        if self.hf_persistence:
            self.hf_persistence.add_document_to_registry_only(
                filename=stored_name,
                source=str(stored_path),
            )

        # 🔑 SINGLE SOURCE OF TRUTH FOR EMBEDDING
        vectorstore = get_vectorstore_manager()
        with open(stored_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        vectorstore.add_documents(
            documents=[content],
            metadatas=[{
                "filename": stored_name,
                "original_name": original_name,
                "uploaded_at": timestamp,
            }],
            sync_to_hub=False,
        )

        print(f"[FILE_MANAGER] ✅ Uploaded + embedded: {stored_name}")
        return file_info

    # ------------------------------------------------------------------
    # READ / RENDER
    # ------------------------------------------------------------------

    def get_files(self) -> List[Dict[str, str]]:
        return self._files

    def render_files_text(self) -> str:
        if not self._files:
            return "📂 No files uploaded yet"

        return "\n".join(
            f"{i+1}. **{f['name']}** ({f.get('size_kb', 0)} KB)"
            for i, f in enumerate(self._files)
        )

    def get_storage_info(self) -> Dict:
        total_size = sum(f.get("size", 0) for f in self._files)
        return {
            "file_count": len(self._files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "storage_path": str(self.storage_dir),
        }

    def render_storage_summary(self) -> str:
        #
        # Render a human-readable storage summary for UI display.
        #
        # Returns:
        #     str: Human-readable storage summary
        #
        info = self.get_storage_info()

        if info["file_count"] == 0:
            return "📂 No documents in RAG storage"

        return (
            f"📄 Documents: {info['file_count']}\n"
            f"💾 Total size: {info['total_size_mb']} MB\n"
            f"📁 Storage path: {info['storage_path']}"
        )
    

    # ------------------------------------------------------------------
    # DELETE / CLEAR
    # ------------------------------------------------------------------

    def clear_all_files(self) -> int:
        count = 0
        self._files = []

        for file_path in self.storage_dir.iterdir():
            if file_path.is_file() and file_path.name != ".gitkeep":
                file_path.unlink()
                count += 1

        get_vectorstore_manager().clear()

        if self.hf_persistence:
            self.hf_persistence.clear_registry()

        print(f"[FILE_MANAGER] 🗑️ Cleared {count} file(s)")
        return count


# ------------------------------------------------------------------
# SINGLETON
# ------------------------------------------------------------------

_file_manager_instance = None

def get_file_manager() -> FileManager:
    global _file_manager_instance
    if _file_manager_instance is None:
        _file_manager_instance = FileManager()
    return _file_manager_instance

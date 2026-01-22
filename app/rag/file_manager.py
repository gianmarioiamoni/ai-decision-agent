# app/rag/file_manager.py

# RAG File Manager - Enterprise-Grade State Management for Context Documents.

# ARCHITECTURE:
# - FileManager is a stateful singleton (single source of truth)
# - Maintains internal file list (self._files)
# - Provides pure functions for UI rendering
# - Guarantees consistency across UI reloads
# Storage configuration - USE ABSOLUTE PATH
#
# Args:
#     PROJECT_ROOT: Path to the project root
#
# Returns:
#     Path to the project root
#

import os
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

# Import HF persistence for cloud storage
try:
    from app.rag.hf_persistence import get_hf_persistence
    HF_PERSISTENCE_AVAILABLE = True
    print("[FILE_MANAGER] ✅ HF persistence module imported successfully")
except Exception as e:
    HF_PERSISTENCE_AVAILABLE = False
    print(f"[FILE_MANAGER] ⚠️ HF persistence not available: {e}")
    print("[FILE_MANAGER] Using local storage only")


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAG_STORAGE_DIR = PROJECT_ROOT / "data" / "uploaded_rag"

try:
    RAG_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[FILE_MANAGER] RAG Storage Directory: {RAG_STORAGE_DIR}")
except Exception as e:
    print(f"[FILE_MANAGER] ⚠️ Warning: Could not create RAG storage directory: {e}")
    print(f"[FILE_MANAGER] RAG Storage Directory (not writable): {RAG_STORAGE_DIR}")


class FileManager:
    #   
    # Stateful file manager for RAG context documents.
    #
    # This class maintains the list of uploaded files as internal state
    # and provides methods to manipulate and query that state.
    #
    # Args:
    #     storage_dir: Directory for file storage (defaults to project data/uploaded_rag/)
    #
    # Returns:
    #     FileManager instance
    #
    def __init__(self, storage_dir: Path = RAG_STORAGE_DIR):
        #
        # Initialize FileManager with storage directory.
        #
        # Args:
        #     storage_dir: Directory for file storage (defaults to project data/uploaded_rag/)
        #
        self.storage_dir = storage_dir
        self._files: List[Dict[str, str]] = []
        
        # Try to initialize HF persistence
        try:
            self.hf_persistence = get_hf_persistence() if HF_PERSISTENCE_AVAILABLE else None
            if self.hf_persistence:
                print("[FILE_MANAGER] ✅ HF persistence instance created")
        except Exception as e:
            print(f"[FILE_MANAGER] ⚠️ Could not create HF persistence: {e}")
            self.hf_persistence = None
        
        try:
            # On HF Spaces, load from HF Hub instead of local filesystem
            if self.hf_persistence:
                print("[FILE_MANAGER] 🌐 Using HF Hub for storage")
                self._load_from_hf_hub()
            else:
                # Fallback to local filesystem (development mode)
                print("[FILE_MANAGER] 💾 Using local filesystem for storage")
                self.storage_dir.mkdir(parents=True, exist_ok=True)
                self.refresh_state()
            
            print(f"[FILE_MANAGER] 🏗️ FileManager initialized with {len(self._files)} file(s)")
        except Exception as e:
            print(f"[FILE_MANAGER] ⚠️ Warning during initialization: {e}")
            import traceback
            traceback.print_exc()
            print(f"[FILE_MANAGER] 🏗️ FileManager initialized with 0 file(s) (filesystem access limited)")
    
    def _load_from_hf_hub(self):
        #
        # Load file registry from HF Hub (for HF Spaces deployment)
        #
        print(f"\n[FILE_MANAGER] 📥 Loading file registry from HF Hub...")
        
        try:
            if not self.hf_persistence:
                print(f"[FILE_MANAGER] ⚠️ HF persistence not available")
                self._files = []
                return
            
            registry = self.hf_persistence.load_registry()
            
            # Convert registry format to internal _files format
            self._files = [
                {
                    "name": doc.get("filename", "unknown"),
                    "path": doc.get("source", ""),
                    "size": 0,  # Size not tracked in registry
                    "size_kb": 0.0,
                    "modified": doc.get("uploaded_at", "N/A"),
                    "timestamp": 0  # Timestamp not tracked
                }
                for doc in registry
                if doc and isinstance(doc, dict) and "filename" in doc
            ]
            
            print(f"[FILE_MANAGER] ✅ Loaded {len(self._files)} file(s) from HF Hub")
        except Exception as e:
            print(f"[FILE_MANAGER] ⚠️ Error loading from HF Hub: {e}")
            import traceback
            traceback.print_exc()
            self._files = []
    
    def refresh_state(self) -> List[Dict[str, str]]:
        #
        # Reload file list from disk or HF Hub and update internal state.
        #
        # Returns:
        #     Updated list of files
        #
        print(f"\n[FILE_MANAGER] 🔄 refresh_state() called")
        
        self._files = []
        
        # On HF Spaces, load from HF Hub
        if self.hf_persistence:
            self._load_from_hf_hub()
            return self._files
        
        # Fallback to local filesystem (development mode)
        try:
            if not self.storage_dir.exists():
                print(f"[FILE_MANAGER] ⚠️ Storage directory does not exist: {self.storage_dir}")
                return self._files
            
            for file_path in self.storage_dir.iterdir():
                if file_path.is_file() and file_path.name != '.gitkeep':
                    try:
                        stat = file_path.stat()
                        self._files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": stat.st_size,
                            "size_kb": round(stat.st_size / 1024, 2),
                            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            "timestamp": stat.st_mtime
                        })
                    except Exception as e:
                        print(f"[FILE_MANAGER] ⚠️ Error reading file {file_path}: {e}")
            
            # Sort by modification time (newest first)
            self._files.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
            
            print(f"[FILE_MANAGER] 📊 State refreshed: {len(self._files)} file(s)")
        except Exception as e:
            print(f"[FILE_MANAGER] ⚠️ Error during refresh_state: {e}")
        
        return self._files
    
    def get_files(self) -> List[Dict[str, str]]:
        #
        # Get current file list (state).
        #
        # Returns:
        #     Current list of files from internal state
        #
        return self._files
    
    def get_storage_info(self) -> Dict:
        #
        # Get storage statistics from current state.
        #
        # Returns:
        #     Dict with 'file_count', 'total_size_mb', etc.
        #
        try:
            if not self._files:
                total_size = 0
            else:
                total_size = sum(f.get("size", 0) for f in self._files)
            
            return {
                "file_count": len(self._files) if self._files else 0,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "storage_path": str(self.storage_dir.absolute())
            }
        except Exception as e:
            print(f"[FILE_MANAGER] ⚠️ Error in get_storage_info: {e}")
            return {
                "file_count": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
                "storage_path": str(self.storage_dir.absolute())
            }
    
    def render_files_text(self) -> str:
        #
        # Pure function: render file list as formatted text.
        #
        #     This is a pure UI rendering function with no side effects.
        #
        # Returns:
        #     Formatted text for Gradio Textbox
        #
        try:
            if not self._files:
                return "📂 No files uploaded yet"
            
            lines = [
                f"{i+1}. **{f['name']}** ({f.get('size_kb', 0)} KB) • {f.get('modified', 'N/A')}"
                for i, f in enumerate(self._files)
            ]
            
            return "\n".join(lines)
        except Exception as e:
            print(f"[FILE_MANAGER] ⚠️ Error in render_files_text: {e}")
            return "⚠️ Error loading file list"
    
    def render_storage_summary(self) -> str:
        #
        # Pure function: render storage summary.
        #
        # Returns:
        #     Formatted storage summary
        #
        try:
            info = self.get_storage_info()
            return (
                f"📊 **Storage:** {info['file_count']} file(s) • "
                f"{info['total_size_mb']} MB"
            )
        except Exception as e:
            print(f"[FILE_MANAGER] ⚠️ Error in render_storage_summary: {e}")
            return "📊 **Storage:** 0 file(s) • 0.0 MB"
    
    def save_uploaded_file(self, file_path: str) -> Dict[str, str]:
        #
        # Save an uploaded file and update state.
        #
        # Args:
        #     file_path: Path to the temporary uploaded file (from Gradio)
        #
        # Returns:
        #     Dict with file metadata
        #
        # Raises:
        #     FileNotFoundError: If source file doesn't exist
        #
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        
        # Extract original filename
        original_name = Path(file_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create unique filename: originalname_timestamp.ext
        name_parts = original_name.rsplit('.', 1)
        if len(name_parts) == 2:
            base_name, ext = name_parts
            stored_name = f"{base_name}_{timestamp}.{ext}"
        else:
            stored_name = f"{original_name}_{timestamp}"
        
        stored_path = self.storage_dir / stored_name
        
        # Copy file to permanent storage
        shutil.copy2(file_path, stored_path)
        
        print(f"✅ [FILE_MANAGER] Saved: {original_name} → {stored_name}")
        
        # Refresh state to include new file
        self.refresh_state()
        
        return {
            "original_name": original_name,
            "stored_path": str(stored_path),
            "stored_name": stored_name,
            "timestamp": timestamp
        }
    
    def read_file_content(self, file_path: str) -> str:
        #
        # Read content from a stored file.
        #
        # Args:
        #     file_path: Path to the stored file
        #
        # Returns:
        #     File content as string
        #
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def read_all_contents(self) -> List[str]:
        #
        # Read content from all stored files.
        #
        # Returns:
        #     List of file contents as strings
        #
        contents = []
        
        for file_info in self._files:
            try:
                content = self.read_file_content(file_info["path"])
                if content.strip():
                    contents.append(content)
            except Exception as e:
                print(f"⚠️ [FILE_MANAGER] Error reading {file_info['name']}: {e}")
                continue
        
        return contents
    
    def delete_file(self, file_name: str) -> bool:
        #
        # Delete a specific file and update state.
        #
        # Args:
        #     file_name: Name of the file to delete
        #
        # Returns:
        #     True if deleted successfully
        #
        
        file_path = self.storage_dir / file_name
        
        if file_path.exists() and file_path.is_file():
            file_path.unlink()
            print(f"🗑️ [FILE_MANAGER] Deleted: {file_name}")
            self.refresh_state()
            return True
        else:
            print(f"⚠️ [FILE_MANAGER] File not found: {file_name}")
            return False
    
    def clear_all_files(self) -> int:
        #
        # Delete all files (except .gitkeep) and update state.
        #
        # Returns:
        #     Number of files deleted
        #
        count = 0
        
        for file_path in self.storage_dir.iterdir():
            if file_path.is_file() and file_path.name != '.gitkeep':
                file_path.unlink()
                count += 1
        
        print(f"🗑️ [FILE_MANAGER] Cleared {count} file(s)")
        self.refresh_state()
        
        return count


# Singleton instance for global access
_file_manager_instance = None

def get_file_manager() -> FileManager:
    #
    # Get the singleton FileManager instance.
    #
    # Returns:
    #     Global FileManager instance
    #

    global _file_manager_instance
    if _file_manager_instance is None:
        _file_manager_instance = FileManager()
    return _file_manager_instance


# Legacy functions for backward compatibility (delegate to singleton)
def load_all_files() -> List[Dict[str, str]]:
    # Legacy function - use get_file_manager().get_files() instead.
    
    return get_file_manager().get_files()

def save_uploaded_file(file_path: str) -> Dict[str, str]:
    # Legacy function - use get_file_manager().save_uploaded_file() instead.

    return get_file_manager().save_uploaded_file(file_path)

def read_all_contents() -> List[str]:
    # Legacy function - use get_file_manager().read_all_contents() instead."""
    return get_file_manager().read_all_contents()

def clear_all_files() -> int:
   # Legacy function - use get_file_manager().clear_all_files() instead."""
    return get_file_manager().clear_all_files()

def get_storage_info() -> Dict:
    # Legacy function - use get_file_manager().get_storage_info() instead."""
    return get_file_manager().get_storage_info()

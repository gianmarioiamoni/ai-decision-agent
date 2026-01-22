# app/ui/handlers/loaders/context_logger.py
#
# Logger for context document loading operations.
# Separated from loading logic following SRP.
#

from typing import List


class ContextLogger:
    """
    Log context document loading operations.
    
    Responsibility: Single purpose - log/debug information about loaded documents.
    No I/O operations, pure logging/presentation.
    """
    
    def log_loading_summary(self, docs: List[str], storage_info: dict) -> None:
        """
        Log comprehensive summary of loaded documents.
        
        Args:
            docs: List of loaded document contents
            storage_info: Dictionary with storage information
        """
        print("\n📂 Loading ALL files from permanent storage...")
        
        # RAG DEBUG - File Loading Summary
        print("\n" + "="*60)
        print("🔍 RAG DEBUG - FILE LOADING PHASE")
        print("="*60)
        
        if docs:
            self._log_documents(docs)
        else:
            self._log_no_documents()
        
        self._log_storage_status(storage_info)
        
        print("="*60 + "\n")
    
    def _log_documents(self, docs: List[str]) -> None:
        """
        Log information about loaded documents.
        
        Args:
            docs: List of document contents
        """
        print(f"✅ Loaded {len(docs)} document(s) from storage")
        for i, doc in enumerate(docs, start=1):
            print(f"   📄 Doc {i}: {len(doc)} chars")
            preview = doc[:150].replace('\n', ' ')
            print(f"      Preview: {preview}...")
    
    def _log_no_documents(self) -> None:
        """Log message when no documents are found."""
        print("❌ NO context documents in storage - will use general reasoning ONLY")
        print("   💡 TIP: Upload context files (.txt, .md, .csv) to get context-aware analysis")
    
    def _log_storage_status(self, storage_info: dict) -> None:
        """
        Log storage status information.
        
        Args:
            storage_info: Dictionary with storage statistics
        """
        print(f"\n📊 Storage Status:")
        print(f"   Files: {storage_info.get('file_count', 0)}")
        print(f"   Total size: {storage_info.get('total_size_mb', 0.0)} MB")
        print(f"   Location: {storage_info.get('storage_path', 'Unknown')}")


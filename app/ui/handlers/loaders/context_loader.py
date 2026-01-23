# app/ui/handlers/loaders/context_loader.py
#
# Loader for context documents metadata.
# Note: Actual documents are in persistent vectorstore, not loaded as text.
#

from typing import List
from app.rag.file_manager import get_file_manager, get_storage_info


class ContextLoader:
    """
    Provide context document metadata for prompt builders.
    
    Responsibility: Signal whether documents exist (for prompt mode selection).
    Actual document content is in vectorstore, not loaded here.
    """
    
    def load(self):
        """
        Get placeholder list indicating if documents exist.
        
        This is used by prompt builders to decide between:
        - "grounded" mode (documents exist)
        - "generic" mode (no documents)
        
        Returns:
            List of empty strings (one per document) to signal document count
        """
        file_manager = get_file_manager()
        file_count = len(file_manager._files)
        
        # Return empty strings as placeholders (one per file)
        # Prompt builders only check if list is empty or not
        return ["" for _ in range(file_count)]
    
    def get_storage_info(self) -> dict:
        """
        Get information about storage status.
        
        Returns:
            Dictionary with storage information (file_count, total_size_mb, etc.)
        """
        return get_storage_info()


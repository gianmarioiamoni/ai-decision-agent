# app/ui/handlers/loaders/context_loader.py
#
# Loader for context documents from permanent storage.
# Pure I/O operation without logging concerns.
#

from typing import List
from app.rag.file_manager import read_all_contents, get_storage_info


class ContextLoader:
    """
    Load context documents from permanent storage.
    
    Responsibility: Single purpose - load documents from filesystem.
    No logging, no formatting, pure I/O.
    """
    
    def load(self):
        """
        Load all context documents from permanent storage.
        
        Returns:
            List of document content strings
        """
        return read_all_contents()
    
    def get_storage_info(self) -> dict:
        """
        Get information about storage status.
        
        Returns:
            Dictionary with storage information (file_count, total_size_mb, etc.)
        """
        return get_storage_info()


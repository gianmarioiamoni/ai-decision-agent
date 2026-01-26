# app/ui/handlers/loaders/context_loader.py
#
# Loader for context documents metadata.
# Note: Actual documents are stored in the persistent vectorstore.
#

from typing import List
from app.rag.file_manager import get_file_manager


class ContextLoader:
    #
    # Provide context document presence information for prompt builders.

    # Responsibilities:
    # - Signal whether RAG documents exist
    # - Do NOT load document content
    # - Do NOT expose storage or filesystem details

    def load(self) -> List[str]:
        #
        # Return placeholder list indicating whether documents exist.

        # Used by prompt builders to choose between:
        # - grounded mode (documents present)
        # - generic mode (no documents)

        # Returns:
        #     List[str]: empty strings, one per document
        #
        file_manager = get_file_manager()
        file_count = len(file_manager.get_files())

        # Placeholder list — content is irrelevant
        return ["" for _ in range(file_count)]


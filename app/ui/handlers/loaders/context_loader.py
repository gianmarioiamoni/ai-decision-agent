# app/ui/handlers/loaders/context_loader.py
#
# Loader for context documents metadata.
# Note: Actual documents are stored in the persistent vectorstore.
#

import os
from typing import List
from app.rag.file_manager import get_file_manager


class ContextLoader:
    #
    # Provide context document presence information for prompt builders.
    #
    # Responsibilities:
    # - Signal whether RAG documents exist
    # - Do NOT load document content
    # - Do NOT expose storage or filesystem details
    # - Read REAL files only
    # - Never download at runtime
    # - Empty or missing files disable RAG implicitly
    #

    def load(self) -> List[str]:
        #
        # Return placeholder list indicating whether documents exist.
        #
        # Used by prompt builders to choose between:
        # - grounded mode (documents present)
        # - generic mode (no documents)
        #
        # Returns:
        #     List[str]: empty strings, one per document
        #
        file_manager = get_file_manager()

        docs = []
        files = file_manager.get_files()

        print("\n============================================================")
        print("🔍 RAG DEBUG - FILE LOADING PHASE")
        print("============================================================")

        for f in files:
            name = f.get("name")
            path = f.get("path")

            if not path or not os.path.exists(path):
                print(f"❌ Skipping missing or invalid file: {name}")
                continue

            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()

            if not content.strip():
                print(f"❌ Skipping empty file: {name}")
                continue
            
            docs.append(content)

            preview = content[:80].replace("\n", "").strip()
            print(f"✅ Loaded {name} ({len(content)} chars)")
            print(f"📝 Preview: '{preview}'")

        print("\n============================================================")
        print("🔍 RAG DEBUG - FINAL CONTEXT")
        print("============================================================")
        print(f"📄 Total files loaded: {len(docs)}")
        print(f"📄 Total characters: {sum(len(d) for d in docs)}")

        return docs


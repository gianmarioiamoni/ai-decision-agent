import os
from app.rag.file_manager import get_file_manager


class ContextLoader:
    #
    # Loads REAL, LOCAL, NON-EMPTY RAG documents.
    #
    # No HF.
    # No downloads.
    # No vectorstore.
    #

    def load(self) -> list[str]:
        file_manager = get_file_manager()
        files = file_manager.get_files()

        docs: list[str] = []

        for f in files:
            name = f.get("name")
            path = (
                f.get("path")
                or f.get("full_path")
                or f.get("local_path"))

            if not path or not os.path.exists(path):
                print(f"[RAG LOADER] ⚠️ Missing file skipped: {name}")
                continue

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                    content = fh.read().strip()

                if not content:
                    print(f"[RAG LOADER] ⚠️ Empty file skipped: {name}")
                    continue

                docs.append(content)

            except Exception as e:
                print(f"[RAG LOADER] ❌ Failed reading {name}: {e}")

        return docs

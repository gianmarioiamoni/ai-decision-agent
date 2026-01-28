# app/rag/bootstrap.py

# One-time RAG bootstrap (READ-ONLY).
#
# Responsibilities:
# - Load FileManager registry
# - Initialize Vectorstore
#
# MUST NOT:
# - Download files
# - Create embeddings
# - Modify RAG state
#
from app.rag.file_manager import get_file_manager
from app.rag.vectorstore_manager import get_vectorstore_manager

_RAG_BOOTSTRAPPED = False

def bootstrap_rag():
    global _RAG_BOOTSTRAPPED
    if _RAG_BOOTSTRAPPED:
        print("[RAG BOOTSTRAP] ⚠️ Already bootstrapped")
        return

    print("[RAG BOOTSTRAP] 🚀 RAG BOOTSTRAP START")

    file_manager = get_file_manager()
    vectorstore_manager = get_vectorstore_manager()

    # 1️⃣ Load registry ONLY
    files = file_manager.refresh_state()
    print(f"[RAG BOOTSTRAP] 📄 Registry loaded: {len(files)} file(s)")

    # 2️⃣ Init vectorstore ONLY (no embeddings)
    vectorstore_manager.get_vectorstore()
    print("[RAG BOOTSTRAP] 📦 Vectorstore initialized")

    # 3️⃣ Log state — NO ACTIONS
    embedding_count = vectorstore_manager.count()
    print(
        f"[RAG BOOTSTRAP] ℹ️ Bootstrap state: "
        f"files={len(files)}, embeddings={embedding_count}"
    )

    _RAG_BOOTSTRAPPED = True
    print("[RAG BOOTSTRAP] ✅ RAG bootstrap completed (read-only)")

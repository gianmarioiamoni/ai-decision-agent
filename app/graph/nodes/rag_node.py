# /app/graph/nodes/rag_node.py
# Node to integrate Hybrid RAG support: contextual documents retrieval

from typing import Dict
from app.graph.state import DecisionState
from app.rag.vectorstore_manager import get_vectorstore_manager
from langchain_core.messages import AIMessage


def rag_node(state: DecisionState) -> Dict:
    #
    # Retrieve relevant information from persistent vectorstore for Hybrid RAG.
    #
    # Returns:
    # - rag_context: formatted authoritative context for LLM
    # - messages: LangChain messages for conversation traceability
    #

    vectorstore_manager = get_vectorstore_manager()
    vectorstore = vectorstore_manager.get_vectorstore()

    # --------------------------------------------------
    # SAFETY CHECK: no embeddings
    # --------------------------------------------------
    try:
        if not vectorstore_manager.has_documents():
            return {
                "rag_context": "",
                "messages": [
                    AIMessage(
                        content="📄 No RAG context available. Using general knowledge only."
                    )
                ],
            }

    except Exception as e:
        print(f"[RAG_NODE] ⚠️ Vectorstore check failed: {e}")
        return {
            "rag_context": "",
            "messages": [
                AIMessage(
                    content="📄 RAG unavailable due to internal error. Using general knowledge only."
                )
            ],
        }

    # --------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------
    question = state.get("question", "")

    print("\n" + "=" * 60)
    print("🔍 RAG DEBUG - RETRIEVAL PHASE")
    print("=" * 60)
    print(f"📝 Question: {question}")
    print("🎯 Retrieving top-5 most relevant chunks from persistent vectorstore...")

    retrieved = vectorstore.similarity_search_with_score(question, k=5)

    print(f"✅ Retrieved {len(retrieved)} chunks")
    for i, (doc, score) in enumerate(retrieved, start=1):
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"\n📄 Chunk {i} (distance: {score:.4f})")
        print(f"   {preview}...")
    print("=" * 60 + "\n")

    # --------------------------------------------------
    # BUILD AUTHORITATIVE RAG CONTEXT
    # --------------------------------------------------
    rag_context = "Use the following chunks in priority order (most relevant first):\n\n"
    unique_sources = set()

    for i, (doc, score) in enumerate(retrieved, start=1):
        doc_source = doc.metadata.get(
            "filename", doc.metadata.get("source", f"Document_{i}")
        )
        chunk_id = doc.metadata.get("chunk_id", i)

        unique_sources.add(doc_source)

        # Convert distance to similarity (0–1)
        similarity = max(0.0, min(1.0, 1 - min(score, 1.0)))

        rag_context += (
            f"[CHUNK {i}] Source: {doc_source} | Chunk ID: {chunk_id} | "
            f"Similarity: {similarity:.2f}\n"
            f"ORGANIZATIONAL FACT:\n{doc.page_content}\n\n"
        )

    num_documents = len(unique_sources)

    # --------------------------------------------------
    # RETURN (STRICTLY LangChain messages)
    # --------------------------------------------------
    return {
        "rag_context": rag_context.strip(),
        "messages": [
            AIMessage(
                content=(
                    f"📄 RAG Context: Retrieved {len(retrieved)} authoritative chunks "
                    f"from {num_documents} uploaded document(s)."
                )
            )
        ],
    }


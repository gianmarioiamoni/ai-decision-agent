# app/graph/nodes/rag_node.py

from app.graph.state import DecisionState
from app.rag.vectorstore_manager import get_vectorstore_manager


def rag_node(state: DecisionState) -> DecisionState:
    #
    # Retrieve relevant information from persistent vectorstore for Hybrid RAG.
    #

    vectorstore_manager = get_vectorstore_manager()
    vectorstore = vectorstore_manager.get_vectorstore()

    # --------------------------------------------------
    # SAFETY CHECK: no embeddings
    # --------------------------------------------------
    try:
        if not vectorstore_manager.has_documents():
            state["authoritative_context"] = []
            state["general_context"] = []
            state["query_similarity"] = []
            return state

    except Exception as e:
        print(f"[RAG_NODE] ⚠️ Vectorstore check failed: {e}")
        state["authoritative_context"] = []
        state["general_context"] = []
        state["query_similarity"] = []
        return state

    # --------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------
    question = state["user_query"]

    print("\n" + "=" * 60)
    print("🔍 RAG DEBUG - RETRIEVAL PHASE")
    print("=" * 60)
    print(f"📝 Question: {question}")
    print("🎯 Retrieving top-5 most relevant chunks from persistent vectorstore...")

    retrieved = vectorstore.similarity_search_with_score(question, k=5)

    print(f"✅ Retrieved {len(retrieved)} chunks")

    authoritative_chunks: list[str] = []
    similarity_scores: list[float] = []

    for i, (doc, score) in enumerate(retrieved, start=1):
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"\n📄 Chunk {i} (distance: {score:.4f})")
        print(f"   {preview}...")

        raw_similarity = 1.0 - score
        similarity = max(0.0, min(1.0, raw_similarity))

        authoritative_chunks.append(doc.page_content)
        similarity_scores.append(similarity)

    print("=" * 60 + "\n")

    # --------------------------------------------------
    # UPDATE STATE
    # --------------------------------------------------
    state["authoritative_context"] = authoritative_chunks
    state["query_similarity"] = similarity_scores

    return state


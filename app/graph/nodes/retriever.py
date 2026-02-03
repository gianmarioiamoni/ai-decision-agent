# app/graph/nodes/retriever.py

from app.rag.vectorstore_manager import get_vectorstore_manager
from app.graph.state import DecisionState


def retriever_node(state: DecisionState) -> DecisionState:
    #
    # Retrieves supportive evidence from the vectorstore based on
    # the user question and the generated analysis plan.
    #
    # IMPORTANT:
    # - Technical node
    # - No messages
    # - No authoritative RAG context
    #

    try:
        vectorstore_manager = get_vectorstore_manager()
        vectorstore = vectorstore_manager.get_vectorstore()
    except Exception as e:
        print(f"[RETRIEVER_NODE] ❌ Vectorstore init failed: {e}")
        state.general_context = []
        return state

    if not state.user_query:
        raise ValueError("Retriever node requires a valid user query")

    # Build retrieval query
    query = state.user_query

    # Perform similarity search
    docs = vectorstore.similarity_search(query, k=5)

    # Extract page content
    retrieved_docs = [doc.page_content for doc in docs]

    print(
        f"[RETRIEVER_NODE] 📚 Retrieved {len(retrieved_docs)} evidence chunks"
    )

    # Supportive (non-authoritative) context
    state.general_context = retrieved_docs

    return state


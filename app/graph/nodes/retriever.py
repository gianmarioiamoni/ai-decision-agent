# app/graph/nodes/retriever.py
from typing import Dict, List

from app.graph.state import DecisionState
from app.rag.vectorstore_manager import get_vectorstore_manager


# Retriever node
# This node retrieves relevant documents from ChromaDB
# based on the question and the generated plan.
#
# IMPORTANT:
# - This is a TECHNICAL node
# - It MUST NOT emit chat messages
# - It only enriches the shared state with retrieved evidence
#
def retriever_node(state: DecisionState) -> Dict:
    #
    # Retrieves relevant documents from the vectorstore based on the question and the generated plan.
    #
    # Args:
    #     state: DecisionState containing the question and the generated plan
    #
    # Returns:
    #     Dict containing retrieved documents ONLY
    #

    try:
        vectorstore_manager = get_vectorstore_manager()
        vectorstore = vectorstore_manager.get_vectorstore()
    except Exception as e:
        print(f"[RETRIEVER_NODE] ❌ Vectorstore init failed: {e}")
        return {
            "retrieved_docs": [],
        }

    question = state.get("question")
    plan = state.get("plan")

    if not question:
        raise ValueError("Retriever node requires a valid question in state")

    # Build retrieval query
    # Plan is used to enrich semantic search when available
    if plan:
        query = f"Question: {question}\n\nRelevant reasoning plan:\n{plan}"
    else:
        query = question

    # Perform similarity search
    docs = vectorstore.similarity_search(query, k=5)

    # Extract page content
    retrieved_docs: List[str] = [doc.page_content for doc in docs]

    print(
        f"[RETRIEVER_NODE] 📚 Retrieved {len(retrieved_docs)} evidence chunks"
    )

    # IMPORTANT:
    # - Do NOT touch rag_context
    # - Do NOT emit messages
    # - Retrieved docs are SUPPORTIVE evidence only
    return {
        "retrieved_docs": retrieved_docs,
    }

# app/graph/nodes/retriever.py
from typing import Dict, List

from app.graph.state import DecisionState
from app.rag.vectorstore_manager import get_vectorstore_manager


# Retriever node
# This node retrieves relevant documents from ChromaDB
# based on the question and the generated plan
def retriever_node(state: DecisionState) -> Dict:
    #
    # Retrieves relevant documents from the vectorstore based on the question and the generated plan.
    #
    # Args:
    #     state: DecisionState containing the question and the generated plan
    #
    # Returns:
    #     Dict containing the retrieved documents and the messages
    #

    try:
        # Get vectorstore from vectorstore_manager
        vectorstore_manager = get_vectorstore_manager()
        vectorstore = vectorstore_manager.get_vectorstore()
    except Exception as e:
        print(f"[RETRIEVER_NODE] ❌ Vectorstore init failed: {e}")
        return {
            "retrieved_docs": [],
            "messages": [
                {
                    "role": "assistant",
                    "content": f"Vectorsotre not available: {e}"
                }
            ]
        }
    
    # Get question and plan from state
    question = state.get("question")
    plan = state.get("plan")

    if not question:
        raise ValueError("Retriever node requires a valid question in state")

    # Build the retrieval query
    # The plan is used to enrich the semantic search when available
    if plan:
        query = f"Question: {question}\n\nRelevant reasoning plan:\n{plan}"
    else:
        query = question

    # Perform similarity search
    docs = vectorstore.similarity_search(query, k=5)

    # Extract page content from retrieved documents
    retrieved_docs: List[str] = [doc.page_content for doc in docs]

    # ⚠️ DO NOT overwrite rag_context here!
    # rag_context is set by rag_node (authoritative user-uploaded documents)
    # retrieved_docs contains historical documents (supportive only)
    
    return {
        "retrieved_docs": retrieved_docs,
        # DON'T TOUCH rag_context - it comes from rag_node
        # Append retrieval summary to messages for traceability
        "messages": [
            {
                "role": "assistant",
                "content": f"📚 Authoritative Context: Retrieved {len(retrieved_docs)} relevant evidence chunks from organizational documents"
            }
        ],
    }

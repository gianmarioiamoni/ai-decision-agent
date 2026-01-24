# app/graph/nodes/retriever.py
from typing import Dict, List

from app.graph.state import DecisionState
from app.rag.file_manager import get_file_manager

# Configuration constants
CHROMA_COLLECTION_NAME = "decision_agent_docs"
CHROMA_PERSIST_DIR = "chroma_db"

# Retriever node
# This node retrieves relevant documents from ChromaDB
# based on the question and the generated plan
def retriever_node(state: DecisionState) -> Dict:
    # Get file manager
    file_manager = get_file_manager()
    vectorstore = file_manager.get_vectorstore()

    if not vectorstore:
        print(f"[RETRIEVER_NODE] ⚠️ No vectorstore found")
        return {
            "retrieved_docs": [],
            "messages": [
                {
                    "role": "assistant",
                    "content": "No vectorstore found"
                }
            ]
        }
    
    question = state.get("question")
    plan = state.get("plan")

    if not question:
        raise ValueError("Retriever node requires a valid question in state")

    # Build the retrieval query
    # The plan is used to enrich the semantic search when available
    if plan:
        query = f"Question: {question}\nPlan: {plan}"
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
                "content": f"📚 Historical Context: Retrieved {len(retrieved_docs)} similar past decisions from memory"
            }
        ],
    }

# app/graph/nodes/retriever.py
from typing import Dict, List
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from app.graph.state import DecisionState

# Configuration constants
CHROMA_COLLECTION_NAME = "decision_agent_docs"
CHROMA_PERSIST_DIR = "chroma_db"

# Retriever node
# This node retrieves relevant documents from ChromaDB
# based on the question and the generated plan
def retriever_node(state: DecisionState) -> Dict:
    # Initialize embeddings and vector store (lazy initialization)
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=CHROMA_PERSIST_DIR,
    )
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

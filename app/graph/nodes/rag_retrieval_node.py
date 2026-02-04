# app/graph/nodes/rag_retrieval_node.py

from app.graph.state import DecisionState
from app.rag.vectorstore_manager import get_vectorstore_manager
from app.rag.context_loader import ContextLoader


def rag_retrieval_node(state: DecisionState) -> DecisionState:
    vectorstore = get_vectorstore_manager()

    if vectorstore.count() == 0:
        # RAG disabled → explicit empty context
        state["authoritative_context"] = []
        state["rag_context"] = ""
        return state

    loader = ContextLoader()
    context_docs = loader.load()

    # Authoritative chunks (already embedded)
    state["authoritative_context"] = context_docs

    # Build formatted RAG context string
    state["rag_context"] = "\n\n".join(
        f"[CHUNK {i+1}]\n{doc}"
        for i, doc in enumerate(context_docs)
    )

    return state

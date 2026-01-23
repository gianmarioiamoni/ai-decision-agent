# /app/graph/nodes/rag_node.py
# Node to integrate Hybrid RAG support: contextual documents retrieval

from typing import Dict
from app.graph.state import DecisionState
from app.rag.vectorstore_manager import get_vectorstore_manager

def rag_node(state: DecisionState) -> Dict:
    # Retrieve relevant information from persistent vectorstore for Hybrid RAG.
    #
    # Args:
    #     state: DecisionState containing the question
    #
    # Returns:
    #     Dict containing 'rag_context': str (textual summary of retrieved chunks)
    #     and a message for traceability
    #
    # Get persistent vectorstore
    vectorstore_manager = get_vectorstore_manager()
    vectorstore = vectorstore_manager.get_vectorstore()
    
    # Check if vectorstore has any documents
    try:
        # Try a test query to check if vectorstore is populated
        test_results = vectorstore.similarity_search("test", k=1)
        if not test_results:
            # Vectorstore is empty
            return {
                "rag_context": "",
                "messages": [
                    {
                        "role": "assistant",
                        "content": "No context documents uploaded. Using general knowledge only."
                    }
                ]
            }
    except Exception as e:
        # Vectorstore not initialized or empty
        print(f"[RAG_NODE] ⚠️ Vectorstore check failed: {e}")
        return {
            "rag_context": "",
            "messages": [
                {
                    "role": "assistant",
                    "content": "No context documents available. Using general knowledge only."
                }
            ]
        }
    
    # Query embedding for the question
    question = state.get("question", "")
    
    # 🔍 RAG DEBUG - Before retrieval
    print("\n" + "="*60)
    print("🔍 RAG DEBUG - RETRIEVAL PHASE")
    print("="*60)
    print(f"📝 Question: {question}")
    print(f"🎯 Retrieving top-5 most relevant chunks from persistent vectorstore...")
    
    # Retrieve top 5 relevant chunks from persistent vectorstore
    retrieved = vectorstore.similarity_search_with_score(question, k=5)
    
    # 🔍 RAG DEBUG - After retrieval
    print(f"✅ Retrieved {len(retrieved)} chunks")
    for i, (doc, score) in enumerate(retrieved, start=1):
        preview = doc.page_content[:150].replace('\n', ' ')
        print(f"\n📄 Chunk {i} (similarity: {score:.4f}, first 150 chars):")
        print(f"   {preview}...")
    print("="*60 + "\n")
    
    # 🆕 Aggregate retrieved chunks with structured cognitive framing
    rag_context = "Use the following chunks in priority order (most relevant first):\n\n"
    unique_sources = set()
    
    for i, (doc, score) in enumerate(retrieved, start=1):
        # Metadata
        doc_source = doc.metadata.get('filename', doc.metadata.get('source', f'Document_{i}'))
        chunk_id = doc.metadata.get('chunk_id', i)
        
        # Track unique document sources
        unique_sources.add(doc_source)
        
        # Converting L2 distance to similarity score (0-1)
        # Lower distance = higher similarity
        similarity = max(0.0, min(1.0, 1 - min(score, 1.0)))
        
        rag_context += f"[CHUNK {i}] Source: {doc_source} | Chunk ID: {chunk_id} | Similarity: {similarity:.2f}\n"
        rag_context += f"ORGANIZATIONAL FACT:\n{doc.page_content}\n\n"
    
    # Count unique documents
    num_documents = len(unique_sources)
    
    return {
        "rag_context": rag_context.strip(),
        "messages": [
            {
                "role": "assistant",
                "content": f"📄 RAG Context: Retrieved {len(retrieved)} authoritative chunks from {num_documents} uploaded document(s)"
            }
        ]
    }

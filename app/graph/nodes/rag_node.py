# /app/graph/nodes/rag_node.py
# Node to integrate Hybrid RAG support: contextual documents retrieval

from typing import Dict, List
from langchain_openai import OpenAIEmbeddings  # ✅ Correct import
from langchain_chroma import Chroma
from app.graph.state import DecisionState

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 100) -> List[str]:
    # Split text into overlapping chunks for better retrieval granularity.
    #
    # Args:
    #     text: Text to chunk
    #     chunk_size: Size of each chunk in characters (300 for better granularity)
    #     overlap: Overlap between chunks (100 to preserve context)
    #
    # Returns:
    #     List of text chunks
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def rag_node(state: DecisionState) -> Dict:
    # Retrieve relevant information from uploaded context documents for Hybrid RAG.
    #
    # Args:
    #     state: DecisionState containing context_docs (list of user-uploaded text)
    #
    # Returns:
    #     Dict containing 'rag_context': str (textual summary of retrieved chunks)
    #     and a message for traceability
    #
    context_docs = state.get("context_docs", [])
    
    if not context_docs:
        # No context provided, return empty string
        return {
            "rag_context": "",
            "messages": [
                {
                    "role": "assistant",
                    "content": "No context documents uploaded. Using general knowledge only."
                }
            ]
        }
    
    # 🆕 Create fresh vectorstore for this invocation (not global)
    embeddings = OpenAIEmbeddings()
    context_vectordb = Chroma(embedding_function=embeddings)
    
    # 🆕 Chunk all documents before adding to vectorstore
    all_chunks = []
    all_metadata = []
    
    for doc_idx, doc in enumerate(context_docs, start=1):
        doc_chunks = chunk_text(doc)
        all_chunks.extend(doc_chunks)
        
        # Add metadata for each chunk (source tracking)
        for chunk_idx in range(len(doc_chunks)):
            all_metadata.append({
                'source': f'ContextDoc_{doc_idx}',
                'chunk_id': chunk_idx + 1,
                'total_chunks': len(doc_chunks)
            })
    
    # Add chunked documents to vectorstore with metadata
    context_vectordb.add_texts(texts=all_chunks, metadatas=all_metadata)
    
    # Query embedding for the question
    question = state.get("question", "")
    
    # 🔍 RAG DEBUG - Before retrieval
    print("\n" + "="*60)
    print("🔍 RAG DEBUG - RETRIEVAL PHASE")
    print("="*60)
    print(f"📝 Question: {question}")
    print(f"📚 Total chunks in vectorstore: {len(all_chunks)}")
    print(f"🎯 Retrieving top-5 most relevant chunks...")
    
    # Retrieve top 5 relevant chunks (increased for better coverage)
    retrieved = context_vectordb.similarity_search_with_score(question, k=5)
    
    # 🔍 RAG DEBUG - After retrieval
    print(f"✅ Retrieved {len(retrieved)} chunks")
    for i, (doc, score) in enumerate(retrieved, start=1):
        preview = doc.page_content[:150].replace('\n', ' ')
        print(f"\n📄 Chunk {i} (similarity: {score:.4f}, first 150 chars):")
        print(f"   {preview}...")
    print("="*60 + "\n")
    
    # 🆕 Aggregate retrieved chunks with structured cognitive framing
    rag_context = "Use the following chunks in priority order (most relevant first):\n\n"
    for i, (doc, score) in enumerate(retrieved, start=1):
        # Metadata
        doc_source = doc.metadata.get('source', f'Document_{i}')
        chunk_id = doc.metadata.get('chunk_id', i)
        
        # Converting L2 distance to similarity score (0-1)
        # Lower distance = higher similarity
        similarity = max(0.0, min(1.0, 1 - min(score, 1.0)))
        
        rag_context += f"[CHUNK {i}] Source: {doc_source} | Chunk ID: {chunk_id} | Similarity: {similarity:.2f}\n"
        rag_context += f"ORGANIZATIONAL FACT:\n{doc.page_content}\n\n"
    
    return {
        "rag_context": rag_context.strip(),
        "messages": [
            {
                "role": "assistant",
                "content": f"📄 RAG Context: Retrieved {len(retrieved)} authoritative chunks from {len(context_docs)} uploaded document(s)"
            }
        ]
    }

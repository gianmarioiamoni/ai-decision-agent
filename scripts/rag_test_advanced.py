# app/ui/rag_test_advanced.py
# Advanced RAG test with improved chunking and structured context

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Ensure OPENAI_API_KEY is loaded
if not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv()

# -----------------------------
# Test Document
# -----------------------------
TEST_DOC = """
Team & Project Context – Internal Technical Overview

The development team is composed of 8 engineers, with a strong focus on frontend and UI-driven applications. 
The stack includes React 18, Next.js 14 (App Router), TypeScript, Tailwind CSS, and Shadcn UI. 
Backend services are primarily built with Node.js and Express, with PostgreSQL as the main database.

Current Project Architecture:
- Monorepo structure with Nx workspace
- Frontend: Next.js 14 App Router, React Server Components where possible
- State Management: Zustand for client state, SWR for server state
- Styling: Tailwind CSS with custom design system
- Testing: Jest, React Testing Library, Playwright for E2E

Team Constraints:
- Limited backend expertise (only 2 engineers comfortable with Node.js)
- High velocity expected (2-week sprints)
- Strong preference for TypeScript-first solutions
- Must maintain compatibility with existing design system

Business Context:
- B2B SaaS product with 5000+ active users
- Performance is critical (target: <2s LCP)
- SEO requirements for marketing pages
- Multi-tenant architecture with role-based access control
"""

CHROMA_COLLECTION = "test_rag_advanced"

print("="*70)
print("🧪 ADVANCED RAG TEST - Improved Chunking & Structured Context")
print("="*70)

# -----------------------------
# Step 1: Chunking with new parameters (300 chars, 100 overlap)
# -----------------------------
print("\n📚 STEP 1: Text Chunking")
print("-"*70)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  # Reduced from 500 for better granularity
    chunk_overlap=100  # Increased from 50 for better context preservation
)
chunks = text_splitter.split_text(TEST_DOC)

print(f"✅ Created {len(chunks)} chunks (was 1 with chunk_size=500)")
for i, chunk in enumerate(chunks, start=1):
    print(f"\n[Chunk {i}] ({len(chunk)} chars)")
    print(f"  Preview: {chunk[:100].replace(chr(10), ' ')}...")

# -----------------------------
# Step 2: Embedding & Vectorstore with Metadata
# -----------------------------
print("\n\n📊 STEP 2: Embedding & Vectorstore with Metadata")
print("-"*70)

embeddings = OpenAIEmbeddings()
print("✅ Initialized OpenAI embeddings")

# Create metadata for each chunk
metadatas = [
    {
        'source': 'TestDocument',
        'chunk_id': i+1,
        'total_chunks': len(chunks)
    }
    for i in range(len(chunks))
]

chroma_db = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    metadatas=metadatas,
    collection_name=CHROMA_COLLECTION
)
print(f"✅ Stored {len(chunks)} chunks in Chroma with metadata")

# -----------------------------
# Step 3: Semantic Retrieval with Scores (top-5)
# -----------------------------
print("\n\n🔍 STEP 3: Semantic Retrieval (top-5 with scores)")
print("-"*70)

query = "What is the team's frontend stack and main constraints?"
print(f"Query: {query}\n")

retrieved_with_scores = chroma_db.similarity_search_with_score(query, k=5)

print(f"✅ Retrieved {len(retrieved_with_scores)} chunks:\n")

for i, (doc, score) in enumerate(retrieved_with_scores, start=1):
    source = doc.metadata.get('source', 'Unknown')
    chunk_id = doc.metadata.get('chunk_id', '?')
    
    print(f"[CHUNK {i}] Source: {source} | Chunk ID: {chunk_id} | Relevance: {score:.4f}")
    print(f"  Content (first 150 chars): {doc.page_content[:150].replace(chr(10), ' ')}...")
    print()

# -----------------------------
# Step 4: Structured RAG Context (as sent to LLM)
# -----------------------------
print("\n🎯 STEP 4: Structured RAG Context (LLM Input)")
print("-"*70)

rag_context = "Use the following chunks in priority order (most relevant first):\n\n"
for i, (doc, score) in enumerate(retrieved_with_scores, start=1):
    doc_source = doc.metadata.get('source', f'Document_{i}')
    chunk_id = doc.metadata.get('chunk_id', i)
    
    # Converting L2 distance to similarity score (0-1)
    similarity = max(0.0, min(1.0, 1 - min(score, 1.0)))
    
    rag_context += f"[CHUNK {i}] Source: {doc_source} | Chunk ID: {chunk_id} | Similarity: {similarity:.2f}\n"
    rag_context += f"ORGANIZATIONAL FACT:\n{doc.page_content}\n\n"

print(rag_context)

print("="*70)
print("✅ Test completed successfully!")
print("="*70)

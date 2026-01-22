from langchain_text_splitters import RecursiveCharacterTextSplitter  # ✅ Updated import
from langchain_chroma import Chroma  # ✅ Updated import
from langchain_openai import OpenAIEmbeddings  # ✅ Updated import

# -----------------------------
# Configurazione
# -----------------------------
TEST_DOC = """
Team & Project Context – Internal Technical Overview
The development team is composed of 8 engineers, with a strong focus on frontend and UI-driven applications...
[aggiungi qui il resto del tuo documento per il test]
"""

CHROMA_COLLECTION_NAME = "rag_test_collection"

# -----------------------------
# Step 1: Split document
# -----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # dimensione chunk in caratteri
    chunk_overlap=50
)
chunks = text_splitter.split_text(TEST_DOC)

print(f"Number of chunks created: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"\nChunk {i+1} (first 100 chars): {chunk[:100]}")

# -----------------------------
# Step 2: Embed chunks
# -----------------------------
embeddings = OpenAIEmbeddings()  # Assicurati di avere OPENAI_API_KEY settata
print("\nEmbedding chunks...")
embedded_vectors = [embeddings.embed_query(chunk) for chunk in chunks]
print(f"Embedded {len(embedded_vectors)} vectors")

# -----------------------------
# Step 3: Store in Chroma
# -----------------------------
chroma_db = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    collection_name=CHROMA_COLLECTION_NAME
)
print(f"\nChroma collection '{CHROMA_COLLECTION_NAME}' created")

# -----------------------------
# Step 4: Test Retrieval
# -----------------------------
query = "Describe the team's frontend stack"
retrieved_docs = chroma_db.similarity_search(query, k=3)

print(f"\nRetrieved {len(retrieved_docs)} chunks for query: '{query}'")
for i, doc in enumerate(retrieved_docs):
    print(f"\nChunk {i+1} (first 200 chars):\n{doc.page_content[:200]}")

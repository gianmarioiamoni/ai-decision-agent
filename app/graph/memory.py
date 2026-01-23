# /app/graph/memory.py
# Module for long-term memory: SQLite storage + Chroma semantic retrieval

import os
import sqlite3
from typing import List, Dict, Optional, Union
from datetime import datetime
import numpy as np

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

# -----------------------------
# Configuration
# -----------------------------
DB_PATH = os.environ.get("MEMORY_DB_PATH", "long_term_memory.db")
CHROMA_DIR = os.environ.get("CHROMA_PERSIST_DIR", "chroma_memory")
EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME", "text-embedding-3-large")

SECTION_NAME = "decisions"

# -----------------------------
# SQLite helper functions
# -----------------------------
def init_db():
    # Initialize SQLite database with decisions table if not exists.
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            plan TEXT,
            analysis TEXT,
            decision TEXT,
            confidence REAL,
            timestamp TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()

def save_decision_to_db(question: str, plan: str, analysis: str, decision: str, confidence: float, embedding: Optional[Union[List[float], np.ndarray]]):
    # Save a decision to SQLite database.
    # Embedding is stored as BLOB for Chroma retrieval.
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Convert embedding to numpy array if it's a list
    if embedding is not None and isinstance(embedding, list):
        embedding = np.array(embedding)
    embedding_bytes = embedding.tobytes() if embedding is not None else None
    c.execute("""
        INSERT INTO decisions (question, plan, analysis, decision, confidence, timestamp, embedding)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (question, plan, analysis, decision, confidence, datetime.utcnow().isoformat(), embedding_bytes))
    conn.commit()
    conn.close()

def get_all_decisions() -> List[Dict]:
    # Retrieve all decisions from SQLite (without embeddings for efficiency)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, question, plan, analysis, decision, confidence, timestamp FROM decisions ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    result = []
    for row in rows:
        result.append({
            "id": row[0],
            "question": row[1],
            "plan": row[2],
            "analysis": row[3],
            "decision": row[4],
            "confidence": row[5],
            "timestamp": row[6]
        })
    return result

# -----------------------------
# Chroma semantic retrieval
# -----------------------------
def init_chroma_vectorstore() -> Chroma:
    # Initialize Chroma vector store for semantic retrieval.
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings, collection_name=SECTION_NAME)
    return vectordb

def add_decision_to_chroma(question: str, decision_id: int, vectordb: Chroma):
    # Add a decision's question embedding to Chroma for semantic retrieval.
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
    vectordb.add_texts(texts=[question], metadatas=[{"decision_id": decision_id}])

def retrieve_similar_decisions(question: str, vectordb: Chroma, top_k: int = 3) -> List[Dict]:
    # Retrieve top-k similar decisions for a new question using Chroma semantic search.
    # Returns list of dicts with decision_id and similarity score.
    # Returns empty list if collection doesn't exist yet (first run).
    
    try:
        results = vectordb.similarity_search_with_score(question, k=top_k)
    except Exception as e:
        # Collection doesn't exist yet (first run) or other error
        print(f"[MEMORY] ⚠️ No historical decisions available yet: {e}")
        return []
    
    similar_decisions = []
    for doc, score in results:
        similar_decisions.append({
            "decision_id": doc.metadata.get("decision_id"),
            "similarity": score,
            "content": doc.page_content
        })
    return similar_decisions

# -----------------------------
# Convenience function to save a decision and update Chroma
# -----------------------------
def save_decision(state, vectordb: Optional[Chroma] = None):
    # Save a decision from a DecisionState to SQLite and optionally to Chroma.
    # Computes embedding for retrieval if vectordb is provided.
    question = state["question"]
    plan = state.get("plan") or ""
    analysis = state.get("analysis") or ""
    decision = state.get("decision") or ""
    confidence = state.get("confidence") or 0.0

    embedding = None
    if vectordb is not None:
        embeddings_model = OpenAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        embedding = embeddings_model.embed_query(question)

    # Save to SQLite
    save_decision_to_db(question, plan, analysis, decision, confidence, embedding)

    # Get last inserted id
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT last_insert_rowid()")
    decision_id = c.fetchone()[0]
    conn.close()

    # Save to Chroma
    if vectordb is not None:
        add_decision_to_chroma(question, decision_id, vectordb)

    return decision_id


# Initialize database on module import
init_db()

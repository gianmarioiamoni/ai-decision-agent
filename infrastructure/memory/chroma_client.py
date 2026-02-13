# infrastructure/memory/chroma_client.py
# 
# This file contains the ChromaDB client for the AI Decision Support Agent.
# It hides CromaDB to the remaining part of the code.
# It is used to persist the historical decisions in the database.
#
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from chromadb.utils import embedding_functions



def get_chroma_collection() -> Collection:
    client = chromadb.Client(
        Settings(
            persist_directory=".chroma",
            anonymized_telemetry=False,
        )
    )

    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

    return client.get_or_create_collection(
        name="historical_decisions_v2",
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"},
    )


# infrastructure/memory/chroma_client.py

# This file contains the ChromaDB client for the AI Decision Support Agent.
# It hides CromaDB to the remaining part of the code.
# It is used to persist the historical decisions in the database.
# 
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection


def get_chroma_collection() -> Collection:
    client = chromadb.Client(
        Settings(
            persist_directory=".chroma",
            anonymized_telemetry=False,
        )
    )

    return client.get_or_create_collection(
        name="historical_decisions",
        metadata={"hnsw:space": "cosine"},
    )

# scripts/reset_historical_memory.py

import chromadb
from chromadb.config import Settings

client = chromadb.Client(
    Settings(
        persist_directory=".chroma",
        anonymized_telemetry=False,
    )
)

client.delete_collection("historical_decisions")

print("Collection historical_decisions deleted.")


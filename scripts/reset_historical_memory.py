from infrastructure.memory.chroma_client import get_chroma_collection

collection = get_chroma_collection()

deleted = collection.delete(where={"context_type": "historical"})
print("Historical decisions deleted")

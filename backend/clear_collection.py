"""
One-time utility to wipe the ChromaDB collection clean.
Run this whenever pdf_parser.py or chunker.py logic changes and you need to
re-ingest PDFs without old/duplicate/broken chunks lingering in the vector
store.

Usage (run from the backend/ folder):
    python clear_collection.py
"""
from app.vectorstore.vector_store import client, CHROMA_COLLECTION_NAME

client.delete_collection(CHROMA_COLLECTION_NAME)
print(f"✅ Deleted collection '{CHROMA_COLLECTION_NAME}'.")
print("Restart the server (uvicorn), then re-upload your PDF(s).")
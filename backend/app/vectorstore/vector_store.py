from typing import List, Dict, Any

import chromadb

from app.config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME
from app.ingestion.chunker import Chunk
# 1. UPDATED IMPORT: Point to your new async functions
from app.ingestion.embedder import embed_texts_async, embed_query_async 

# Create or connect to a local Chroma database
client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))

# Create a collection
collection = client.get_or_create_collection(
    name=CHROMA_COLLECTION_NAME
)

print("✅ ChromaDB initialized successfully!")


# 2. ADDED ASYNC: Make the function asynchronous
async def upsert_chunks(chunks: List[Chunk]) -> None:
    """Embed and upsert a batch of chunks (from one uploaded PDF) into Chroma."""
    if not chunks:
        print("[vector_store] No chunks to upsert.")
        return

    texts = [c.text for c in chunks]
    
    # 3. ADDED AWAIT: Wait for your background thread to finish the math
    embeddings = await embed_texts_async(texts)

    collection.upsert(
        ids=[c.chunk_id for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"manual_name": c.manual_name, "page_number": c.page_number}
            for c in chunks
        ],
    )
    print(f"[vector_store] Upserted {len(chunks)} chunks into '{CHROMA_COLLECTION_NAME}'")


# 4. ADDED ASYNC: Make the query function asynchronous
async def query_manuals(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search the vector store. Returns a list of dicts with text, manual_name,
    page_number, and distance — ready for the agent to cite.
    """
    # 5. ADDED AWAIT: Wait for the query embedding
    query_embedding = await embed_query_async(query_text)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    hits = []
    for i in range(len(results["ids"][0])):
        hits.append(
            {
                "text": results["documents"][0][i],
                "manual_name": results["metadatas"][0][i]["manual_name"],
                "page_number": results["metadatas"][0][i]["page_number"],
                "distance": results["distances"][0][i],
            }
        )
    return hits

sreehari said this is the updated code for vector_store.py, so after u complete chunking u can upload this if u want.
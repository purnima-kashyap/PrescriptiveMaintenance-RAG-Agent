from typing import List, Dict, Any

import chromadb

from app.config import CHROMA_DB_DIR, CHROMA_COLLECTION_NAME
from app.ingestion.chunker import Chunk
from app.ingestion.embedder import embed_texts_async, embed_query_async

client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
collection = client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

print("✅ ChromaDB initialized successfully!")


async def upsert_chunks(chunks: List[Chunk]) -> None:
    """Embed and upsert a batch of chunks into Chroma. Must be awaited."""
    if not chunks:
        print("[vector_store] No chunks to upsert.")
        return

    texts = [c.text for c in chunks]
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


async def query_manuals(query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search the vector store. Must be awaited."""
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

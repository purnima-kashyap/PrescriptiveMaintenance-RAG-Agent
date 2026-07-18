import asyncio
from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it across requests."""
    print(f"[embedder] Loading embedding model: {EMBEDDING_MODEL_NAME}")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


async def embed_texts_async(texts: List[str], batch_size: int = 32) -> List[List[float]]:
    """
    Embed a batch of chunk texts asynchronously.
    Offloads CPU-heavy encoding to a separate thread to prevent blocking FastAPI.
    """
    model = get_embedding_model()
    
    # asyncio.to_thread runs the synchronous model.encode in a background thread
    embeddings = await asyncio.to_thread(
        model.encode,
        texts,
        batch_size=batch_size,          # Prevents memory spikes
        show_progress_bar=False, 
        normalize_embeddings=True
    )
    
    return embeddings.tolist()


async def embed_query_async(query: str) -> List[float]:
    """
    Embed a single search query asynchronously.
    """
    model = get_embedding_model()
    instructed_query = f"Represent this sentence for searching relevant passages: {query}"
    
    embedding = await asyncio.to_thread(
        model.encode,
        [instructed_query],
        normalize_embeddings=True
    )
    
    return embedding[0].tolist()
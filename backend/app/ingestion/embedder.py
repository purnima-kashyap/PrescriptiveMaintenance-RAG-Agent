"""
Embeddings via sentence-transformers (free, local, no API key needed).
Model: BAAI/bge-small-en-v1.5 — good quality/speed tradeoff for a small
free-tier project. Loaded once and cached, since loading the model is
expensive.
"""
from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the embedding model once and reuse it across requests."""
    print(f"[embedder] Loading embedding model: {EMBEDDING_MODEL_NAME}")
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a batch of chunk texts (used when upserting into ChromaDB)."""
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
    return embeddings.tolist()


def embed_query(query: str) -> List[float]:
    """
    Embed a single search query. BGE models perform better on retrieval
    when queries get an instruction prefix (documents don't need one).
    """
    model = get_embedding_model()
    instructed_query = f"Represent this sentence for searching relevant passages: {query}"
    embedding = model.encode([instructed_query], normalize_embeddings=True)
    return embedding[0].tolist()
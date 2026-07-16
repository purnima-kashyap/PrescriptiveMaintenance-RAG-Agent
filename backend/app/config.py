"""
All paths and tunables live here so every module (pdf_parser, chunker,
embedder, vector_store, main) imports from one source of truth.
"""
import os
from pathlib import Path

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
MANUALS_DIR = BASE_DIR / "data" / "manuals"
CHROMA_DB_DIR = BASE_DIR / "app" / "vectorstore" / "chroma_db"

# --- Embedding model ---
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# --- Chunking ---
CHUNK_SIZE = 800          
CHUNK_OVERLAP = 150       

# --- Vector store ---
CHROMA_COLLECTION_NAME = "maintenance_manuals"  

# --- LLM  ---
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

MANUALS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
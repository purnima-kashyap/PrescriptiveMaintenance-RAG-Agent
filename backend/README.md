# Minimum-Viable-Product
The Prescriptive Maintenance RAG Agent is an AI-powered maintenance assistant that helps engineers diagnose industrial equipment issues using Retrieval-Augmented Generation (RAG).

Instead of relying solely on a language model's internal knowledge, the system retrieves relevant information from industrial maintenance manuals and uses it to generate accurate, context-aware repair recommendations.

The project is being developed over four weeks, beginning with the construction of the RAG pipeline and vector database.

## Backend Setup
1. cd backend
2. python -m venv venv
3. venv\Scripts\activate
4. pip install fastapi uvicorn

run : uvicorn app.main:app --reload

## ChromaDB Setup

Follow these steps to install and initialize ChromaDB.

### 1. Activate the virtual environment

### 2. Install ChromaDB

  pip install chromadb langchain-chroma


### 3. Verify the installation

pip show chromadb

If the version number is displayed, ChromaDB has been installed successfully.

### 4. Initialize the local database

Run: python backend/rag/vector_store.py

This will automatically Create the `chroma_db/` directory (if it doesn't already exist)

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

### pdfparser
1. cd backend
2. python -m pip install pymupdf 

### embedder
1. cd backend
2. pip install sentence-transformers 
3. pip install python-multipart

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

## IoT Alert Endpoint

`POST /iot-alert` simulates receiving a real-time telemetry alert from a
factory machine (e.g. an overheating pump or motor). It validates the
incoming data (`machine_id`, `error_code`, `temperature`), automatically
builds a search query from it, searches the ingested manuals, and returns
the most relevant troubleshooting sections — no manual query typing needed.

## Query Generator

`app/query_generate/query_generator.py` dynamically converts a validated
`IoTAlert` into a natural-language search query. It works on whatever fields
exist on the alert (not hardcoded), and adds human-readable symptom terms
(e.g. "overheating", "excessive vibration") based on configurable threshold
rules, so retrieval works whether the manual describes issues by error code
or by plain-language symptoms.

## How to test in `/docs` (Check the response)
http://localhost:8000/docs

**/upload**
Upload a manual first
Click **Choose File** and select a PDF manual

**/query**
Manually search the manuals
Enter a search payload, e.g.:
     {
       "query": "motor overheating troubleshooting",
       "top_k": 5
     }

**/iot-alert**
Send a simulated IoT alert:
Enter a test payload, e.g.:
     {
       "machine_id": "PUMP-01",
       "error_code": "E-404",
       "temperature": 105
     }

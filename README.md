### Prescriptive Maintenance RAG Agent (Industry 5.0)

The **Prescriptive Maintenance RAG Agent** is an AI-powered system that helps maintenance teams quickly diagnose and repair industrial machines. Unlike predictive maintenance, which only detects potential failures, this system provides **step-by-step repair instructions** by searching technical manuals using **Retrieval-Augmented Generation (RAG)**.

When an **IoT alert** (e.g., overheating or an error code) is received, the agent automatically generates a search query, retrieves relevant sections from machinery manuals stored in a **vector database (ChromaDB)**, reasons through the issue using a **LangGraph** agent workflow, and generates a repair plan with:

* Problem diagnosis
* Step-by-step repair procedure
* Required tools
* Required spare parts
* Safety precautions
* Manual name and exact page reference

Before generating a response, the agent also runs deterministic checks to verify whether the exact error code and reported machine actually appear in the manual — reducing the risk of hallucinated or misapplied repair guidance.

### Key Technologies

- **FastAPI** – Backend API development
- **Ollama (Llama 3.1)** – Local Large Language Model (LLM)
- **Sentence Transformers (BAAI/bge-small-en-v1.5)** – Text embeddings
- **ChromaDB** – Vector database for semantic search
- **PyMuPDF (fitz)** – PDF parsing and table-aware text extraction
- **LangGraph** – Agent workflow orchestration
- **Streamlit** – Interactive user interface
- **FastAPI Mock Endpoints** – Manual management and inventory simulation

### Main Goal

Reduce **Mean Time to Repair (MTTR)** by providing accurate, context-aware maintenance instructions while minimizing hallucinations and ensuring every repair recommendation is backed by a cited page in the official manual.
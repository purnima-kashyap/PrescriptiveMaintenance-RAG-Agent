### Short Note: Prescriptive Maintenance RAG Agent (Industry 5.0)

The **Prescriptive Maintenance RAG Agent** is an AI-powered system that helps maintenance teams quickly diagnose and repair industrial machines. Unlike predictive maintenance, which only detects potential failures, this system provides **step-by-step repair instructions** by searching technical manuals using **Retrieval-Augmented Generation (RAG)**.

When an **IoT alert** (e.g., overheating or an error code) is received, the agent retrieves relevant information from machinery manuals stored in a **vector database** (Qdrant/Chroma), reasons through the issue using **LangGraph or Google ADK**, and generates a repair plan with:

* Repair steps
* Required tools
* Spare parts
* Manual page references
* Inventory availability (via a mock API)

### Key Technologies

- **FastAPI** – Backend API development
- **Ollama (Llama 3.2)** – Local Large Language Model (LLM)
- **Sentence Transformers (BAAI/bge-small-en-v1.5)** – Text embeddings
- **ChromaDB** – Vector database for semantic search
- **PyMuPDF (fitz)** – PDF parsing and text extraction
- **LangChain** – RAG pipeline
- **LangGraph** – Agent workflow orchestration
- **Streamlit** – Interactive user interface
- **FastAPI Mock API** – Inventory and tool simulation

### Main Goal

Reduce **Mean Time to Repair (MTTR)** by providing accurate, context-aware maintenance instructions while minimizing hallucinations and ensuring repair guidance is backed by official manuals.

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.ingestion.pdf_parser import parse_pdf_bytes
from app.ingestion.chunker import chunk_pages
from app.vectorstore.vector_store import upsert_chunks, query_manuals as vector_query

app = FastAPI(title="Prescriptive Maintenance RAG Agent")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/")
def root():
    return {"message": "Prescriptive Maintenance RAG Agent is running. Visit /docs to test endpoints."}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_manual(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    manual_name = file.filename.rsplit(".", 1)[0]

    try:
        pages = parse_pdf_bytes(file_bytes, manual_name=manual_name)

        if not pages:
            raise HTTPException(
                status_code=422,
                detail="No extractable text found in this PDF (it may be scanned/image-only).",
            )

        chunks = chunk_pages(pages)
        await upsert_chunks(chunks)          # <-- add "await" here

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")

    return {
        "filename": file.filename,
        "pages_parsed": len(pages),
        "chunks_created": len(chunks),
        "status": "ingested",
    }

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    """Search the ingested manuals for relevant chunks."""
    hits = await vector_query(req.query, top_k=req.top_k)
    return {"query": req.query, "results": hits}
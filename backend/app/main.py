from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.ingestion.pdf_parser import parse_pdf_bytes
from app.ingestion.chunker import chunk_pages
from app.vectorstore.vector_store import upsert_chunks, query_manuals as vector_query

app = FastAPI(title="Prescriptive Maintenance RAG Agent")


@app.get("/")
def root():
    return {"message": "Prescriptive Maintenance RAG Agent is running. Visit /docs to test endpoints."}

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_manual(file: UploadFile = File(...)):
    """
    Dynamic PDF upload: user submits a PDF, it's parsed straight from memory,
    chunked, embedded, and upserted into ChromaDB — nothing is saved to disk.
    """
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
        upsert_chunks(chunks)

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

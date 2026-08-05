import shutil
from app.database import init_db, insert_alert
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from datetime import datetime
from pathlib import Path
from fastapi.responses import FileResponse

from app.ingestion.pdf_parser import parse_pdf_bytes
from app.ingestion.chunker import chunk_pages
from app.vectorstore.vector_store import upsert_chunks, query_manuals as vector_query
from app.models.iot_models import IoTAlert
from app.query_generate.query_generator import generate_query
from app.agent.graph import repair_graph
from app.vectorstore.vector_store import upsert_chunks, query_manuals as vector_query, collection
from app.config import MANUALS_DIR
from typing import List

init_db()
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

    # Save the raw PDF to disk
    saved_path = MANUALS_DIR / file.filename
    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    try:
        pages = parse_pdf_bytes(file_bytes, manual_name=manual_name)
        if not pages:
            saved_path.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail="No extractable text found in this PDF.")

        chunks = chunk_pages(pages)
        await upsert_chunks(chunks)

    except HTTPException:
        raise
    except Exception as e:
        saved_path.unlink(missing_ok=True)
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


@app.post("/iot-alert")
async def receive_iot_alert(alert: IoTAlert):
    """
    Full Prescriptive Maintenance workflow using LangGraph.
    """
    insert_alert(
            machine_id=alert.machine_id, 
            error_code=alert.error_code, 
            temperature=alert.temperature
        )

    state = {
        "alert": alert.model_dump(),
        "query": "",
        "retrieved_context": "",
        "prompt": "",
        "repair_plan": "",
        "inventory": {},
    }

    result = await repair_graph.ainvoke(state)

    return {
        "status": "success",
        "received_alert": result["alert"],
        "generated_query": result["query"],
        "repair_plan": result["repair_plan"],
    }

# ------------------- manuals -----------------------------------
@app.get("/manuals")
def list_manuals():
    """List distinct manuals with page/chunk counts, file size, and upload date."""
    all_data = collection.get()
    manual_stats = {}

    for metadata in all_data["metadatas"]:
        name = metadata["manual_name"]
        page = metadata["page_number"]
        if name not in manual_stats:
            manual_stats[name] = {"chunks": 0, "pages": set()}
        manual_stats[name]["chunks"] += 1
        manual_stats[name]["pages"].add(page)

    manuals = []
    for name, stats in manual_stats.items():
        # find matching file on disk to get size/date
        matching_files = list(MANUALS_DIR.glob(f"{name}.pdf")) or list(MANUALS_DIR.glob(f"{name}*.pdf"))
        file_path = matching_files[0] if matching_files else None

        manuals.append({
            "name": name,
            "chunks": stats["chunks"],
            "pages": len(stats["pages"]),
            "file_size_kb": round(file_path.stat().st_size / 1024, 1) if file_path else None,
            "uploaded_at": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%b %d, %Y %H:%M") if file_path else None,
            "has_file": file_path is not None,
        })

    return {"manuals": manuals}

# view pdf 
@app.get("/manuals/{manual_name}/view")
def view_manual(manual_name: str):
    """Serve the PDF inline so it opens in browser instead of downloading."""
    matching_files = list(MANUALS_DIR.glob(f"{manual_name}.pdf")) or list(MANUALS_DIR.glob(f"{manual_name}*.pdf"))
    if not matching_files:
        raise HTTPException(status_code=404, detail="Original PDF file not found on disk.")

    file_path = matching_files[0]
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{file_path.name}"'},
    )

# Download or preview PDF  
@app.get("/manuals/{manual_name}/download")
def download_manual(manual_name: str):
    """Force a download (attachment) of the original PDF file."""
    matching_files = list(MANUALS_DIR.glob(f"{manual_name}.pdf")) or list(MANUALS_DIR.glob(f"{manual_name}*.pdf"))
    if not matching_files:
        raise HTTPException(status_code=404, detail="Original PDF file not found on disk.")

    file_path = matching_files[0]
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{file_path.name}"'},
    )

# Delete Manual 
@app.delete("/manuals/{manual_name}")
def delete_manual(manual_name: str):
    """Delete all chunks belonging to a specific manual, and its file on disk."""
    all_data = collection.get()
    ids_to_delete = [
        id_ for id_, metadata in zip(all_data["ids"], all_data["metadatas"])
        if metadata["manual_name"] == manual_name
    ]

    if not ids_to_delete:
        raise HTTPException(status_code=404, detail=f"Manual '{manual_name}' not found.")

    collection.delete(ids=ids_to_delete)

    matching_files = list(MANUALS_DIR.glob(f"{manual_name}.pdf")) or list(MANUALS_DIR.glob(f"{manual_name}*.pdf"))
    for f in matching_files:
        f.unlink(missing_ok=True)

    return {"status": "deleted", "manual_name": manual_name, "chunks_removed": len(ids_to_delete)}

# Delete bulk manual 
@app.post("/manuals/bulk-delete")
def bulk_delete_manuals(manual_names: List[str]):
    """Delete multiple manuals at once."""
    results = []
    for name in manual_names:
        try:
            result = delete_manual(name)
            results.append(result)
        except HTTPException as e:
            results.append({"manual_name": name, "status": "error", "detail": e.detail})
    return {"results": results}

@app.get("/alerts")
def get_alert_history():
    import sqlite3
    from app.database import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM alerts
        ORDER BY timestamp DESC
    """)

    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return {"alerts": alerts}

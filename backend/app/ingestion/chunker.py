"""
Chunking with overlapping windows.
Splits each page's text into chunks so context isn't lost across boundaries.
Each chunk gets a DETERMINISTIC id (hash of manual_name + page_number + text)
instead of a random UUID — so re-uploading the same PDF overwrites the same
chunks in ChromaDB instead of creating duplicates.
"""
from dataclasses import dataclass
from typing import List
import hashlib

from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.ingestion.pdf_parser import PageContent


@dataclass
class Chunk:
    chunk_id: str
    manual_name: str
    page_number: int
    text: str


def _make_chunk_id(manual_name: str, page_number: int, text: str) -> str:
    """Deterministic id so the same chunk always gets the same id on re-upload."""
    raw = f"{manual_name}|{page_number}|{text}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def chunk_page(page: PageContent) -> List[Chunk]:
    """Split a single page's text into overlapping chunks."""
    text = page.text
    chunks: List[Chunk] = []

    if len(text) <= CHUNK_SIZE:
        chunks.append(
            Chunk(
                chunk_id=_make_chunk_id(page.manual_name, page.page_number, text),
                manual_name=page.manual_name,
                page_number=page.page_number,
                text=text,
            )
        )
        return chunks

    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(page.manual_name, page.page_number, chunk_text),
                    manual_name=page.manual_name,
                    page_number=page.page_number,
                    text=chunk_text,
                )
            )

        start += CHUNK_SIZE - CHUNK_OVERLAP  # step forward, leaving overlap

    return chunks


def chunk_pages(pages: List[PageContent]) -> List[Chunk]:
    """Chunk every page in a list (i.e. one uploaded PDF)."""
    all_chunks: List[Chunk] = []
    for page in pages:
        all_chunks.extend(chunk_page(page))
    print(f"[chunker] Produced {len(all_chunks)} chunks from {len(pages)} pages")
    return all_chunks
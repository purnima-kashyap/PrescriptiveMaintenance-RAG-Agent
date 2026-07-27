"""
Chunking with overlapping windows.

Table content ([TABLE N] blocks produced by pdf_parser.py) is kept ATOMIC —
never split mid-table — since cutting a troubleshooting table in half
truncates "possible cause" / "corrective action" rows and breaks their
alignment. Regular paragraph text still uses overlapping-window chunking.

Each chunk gets a DETERMINISTIC id (hash of manual_name + page_number + text)
instead of a random UUID — so re-uploading the same PDF overwrites the same
chunks in ChromaDB instead of creating duplicates.
"""
from dataclasses import dataclass
from typing import List
import hashlib
import re

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


def _split_plain_text(text: str) -> List[str]:
    """Sliding-window chunking for non-table plain text only."""
    if not text.strip():
        return []

    if len(text) <= CHUNK_SIZE:
        return [text.strip()]

    parts = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunk_text = text[start:end].strip()
        if chunk_text:
            parts.append(chunk_text)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return parts


def chunk_page(page: PageContent) -> List[Chunk]:
    """
    Split a single page's text into chunks. Table blocks ([TABLE N]) are
    kept whole as single chunks regardless of size. Everything else uses
    normal overlapping-window chunking.
    """
    text = page.text
    chunks: List[Chunk] = []

    segments = re.split(r"(?=\[TABLE \d+\])", text)

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue

        if segment.startswith("[TABLE"):
            chunks.append(
                Chunk(
                    chunk_id=_make_chunk_id(page.manual_name, page.page_number, segment),
                    manual_name=page.manual_name,
                    page_number=page.page_number,
                    text=segment,
                )
            )
        else:
            for part in _split_plain_text(segment):
                chunks.append(
                    Chunk(
                        chunk_id=_make_chunk_id(page.manual_name, page.page_number, part),
                        manual_name=page.manual_name,
                        page_number=page.page_number,
                        text=part,
                    )
                )

    return chunks


def chunk_pages(pages: List[PageContent]) -> List[Chunk]:
    """Chunk every page in a list (i.e. one uploaded PDF)."""
    all_chunks: List[Chunk] = []
    for page in pages:
        all_chunks.extend(chunk_page(page))
    print(f"[chunker] Produced {len(all_chunks)} chunks from {len(pages)} pages")
    return all_chunks
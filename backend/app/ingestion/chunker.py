"""
Chunking with overlapping windows.
Splits each page's text into chunks so context isn't lost across boundaries
(e.g. an error-code table that starts near the bottom of a page). Every chunk
keeps its manual name + page number, which the agent will use later to cite
its source.
"""
from dataclasses import dataclass
from typing import List
import uuid

from app.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.ingestion.pdf_parser import PageContent


@dataclass
class Chunk:
    chunk_id: str
    manual_name: str
    page_number: int
    text: str


def chunk_page(page: PageContent) -> List[Chunk]:
    """Split a single page's text into overlapping chunks."""
    text = page.text
    chunks: List[Chunk] = []

    if len(text) <= CHUNK_SIZE:
        chunks.append(
            Chunk(
                chunk_id=str(uuid.uuid4()),
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
                    chunk_id=str(uuid.uuid4()),
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
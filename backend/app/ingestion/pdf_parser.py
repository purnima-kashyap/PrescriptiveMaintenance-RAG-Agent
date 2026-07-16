
from dataclasses import dataclass
from typing import List

import fitz


@dataclass
class PageContent:
    manual_name: str
    page_number: int  # 1-indexed, human-readable, used for citations
    text: str


def _bbox_overlaps(bbox_a, bbox_b, threshold: float = 0.5) -> bool:
    """
    Check whether bbox_a is substantially contained within bbox_b.
    Used to drop plain-text blocks that actually belong to a detected table,
    so the same content isn't extracted twice in two different (and
    conflicting) orders.
    """
    ax0, ay0, ax1, ay1 = bbox_a
    bx0, by0, bx1, by1 = bbox_b

    inter_x0, inter_y0 = max(ax0, bx0), max(ay0, by0)
    inter_x1, inter_y1 = min(ax1, bx1), min(ay1, by1)

    if inter_x1 <= inter_x0 or inter_y1 <= inter_y0:
        return False

    inter_area = (inter_x1 - inter_x0) * (inter_y1 - inter_y0)
    a_area = max((ax1 - ax0) * (ay1 - ay0), 1e-6)
    return (inter_area / a_area) >= threshold


def _format_table_as_text(rows) -> str:
    """
    Turn a PyMuPDF-extracted table (list of rows, each a list of cell
    strings) into row-preserving text — one line per row, each cell paired
    with its column header. This is what keeps "Possible cause" and
    "Corrective action" aligned to the same malfunction instead of getting
    jumbled across rows.
    """
    if not rows:
        return ""

    header = [str(h).strip() if h else "" for h in rows[0]]
    lines = []

    for row in rows[1:]:
        cells = [str(c).strip().replace("\n", " ") if c else "" for c in row]
        if not any(cells):
            continue

        pairs = []
        for col_name, value in zip(header, cells):
            if value:
                label = col_name if col_name else "Value"
                pairs.append(f"{label}: {value}")

        if pairs:
            lines.append(" | ".join(pairs))

    return "\n".join(lines)


def parse_pdf_bytes(file_bytes: bytes, manual_name: str) -> List[PageContent]:
    """
    Extract text from every page of a PDF given as raw bytes — nothing
    touches disk. Tables are detected and extracted row-by-row separately
    from regular paragraph text.
    """
    pages: List[PageContent] = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    try:
        for page_index in range(len(doc)):
            page = doc[page_index]

            table_texts = []
            table_bboxes = []
            try:
                found_tables = page.find_tables()
                for tab in found_tables.tables:
                    rows = tab.extract()
                    formatted = _format_table_as_text(rows)
                    if formatted:
                        table_texts.append(formatted)
                        table_bboxes.append(tab.bbox)
            except Exception as e:
                print(f"[pdf_parser] Table detection failed on page {page_index + 1}: {e}")

            plain_text_parts = []
            blocks = page.get_text("blocks") 
            for block in blocks:
                block_bbox = block[:4]
                block_text = block[4].strip()

                if not block_text:
                    continue

                overlaps_table = any(
                    _bbox_overlaps(block_bbox, tbbox) for tbbox in table_bboxes
                )
                if overlaps_table:
                    continue

                plain_text_parts.append(block_text)

            combined_parts = []
            if plain_text_parts:
                combined_parts.append("\n".join(plain_text_parts))
            for i, t_text in enumerate(table_texts, start=1):
                combined_parts.append(f"[TABLE {i}]\n{t_text}")

            full_text = "\n\n".join(combined_parts).strip()

            if not full_text:
                continue  # skip blank/scanned pages

            pages.append(
                PageContent(
                    manual_name=manual_name,
                    page_number=page_index + 1,
                    text=full_text,
                )
            )
    finally:
        doc.close()

    return pages
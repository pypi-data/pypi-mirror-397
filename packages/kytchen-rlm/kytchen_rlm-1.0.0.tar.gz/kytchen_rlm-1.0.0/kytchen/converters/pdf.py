from __future__ import annotations

import io

from .pages import join_with_boundaries, parse_pages


def convert_pdf_bytes(data: bytes, pages: str | None = None) -> dict:
    try:
        from pypdf import PdfReader
    except Exception as e:  # pragma: no cover
        raise RuntimeError("PDF conversion requires `pypdf`. Install with `pip install 'kytchen[converters]'`.") from e

    reader = PdfReader(io.BytesIO(data))
    page_count = len(reader.pages)
    selected = parse_pages(pages, page_count)

    pieces: list[tuple[int, str]] = []
    for idx in selected:
        try:
            t = reader.pages[idx].extract_text() or ""
        except Exception:
            t = ""
        t = t.strip()
        pieces.append((idx, t))

    text, boundaries = join_with_boundaries(pieces, separator="\n\n\f\n\n")

    return {
        "type": "pdf",
        "page_count": page_count,
        "selected_pages": [i + 1 for i in selected],
        "text": text,
        "page_boundaries": boundaries,
    }

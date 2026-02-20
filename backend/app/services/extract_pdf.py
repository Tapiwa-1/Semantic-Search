from __future__ import annotations

import fitz


def extract_pdf_pages(path: str) -> list[dict]:
    doc = fitz.open(path)
    pages: list[dict] = []
    for i, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        pages.append({"page": i, "text": text})
    return pages

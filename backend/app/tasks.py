from __future__ import annotations

import hashlib
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path

from flask import current_app
from PIL import Image

from .models import Chunk, Document, JobStatus, db
from .services.embed import embed_image, embed_text
from .services.extract_pdf import extract_pdf_pages
from .services.extract_video import extract_frames, extract_poster
from .services.vector_store import get_vector_store

executor = ThreadPoolExecutor(max_workers=int(os.getenv("INDEXER_WORKERS", "2")))


@lru_cache(maxsize=1)
def get_flask_app():
    from . import create_app

    return create_app()


def enqueue_document_processing(app, document_id: int, job_id: str) -> None:
    executor.submit(process_document, document_id, job_id, app)


def _sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            digest.update(block)
    return digest.hexdigest()


def _update_job(job_id: str, status: str, progress: int, error: str | None = None) -> None:
    job = JobStatus.query.get(job_id)
    if job:
        job.status = status
        job.progress = progress
        job.error = error
        db.session.commit()


def process_document(document_id: int, job_id: str, app=None):
    app = app or get_flask_app()
    with app.app_context():
        doc = Document.query.get(document_id)
        if not doc:
            return

        store = get_vector_store()
        doc.status = "processing"
        db.session.commit()
        _update_job(job_id, "processing", 5)

        try:
            doc.sha256_hash = _sha256(doc.file_path)
            existing = Document.query.filter(
                Document.sha256_hash == doc.sha256_hash,
                Document.id != doc.id,
                Document.status == "ready",
            ).first()
            if existing:
                doc.status = "ready"
                doc.preview_path = existing.preview_path
                db.session.commit()
                _update_job(job_id, "ready", 100)
                return

            preview_dir = Path(current_app.config["PREVIEW_FOLDER"])
            preview_path = str(preview_dir / f"{doc.id}.jpg")

            if doc.doc_type == "image":
                image = Image.open(doc.file_path).convert("RGB")
                image.thumbnail((320, 320))
                image.save(preview_path)
                vector = embed_image(doc.file_path)
                chunk = Chunk(document_id=doc.id, chunk_type="image", ref=None, text_content=None)
                db.session.add(chunk)
                db.session.flush()
                vector_id = f"chunk-{chunk.id}-{uuid.uuid4()}"
                chunk.vector_id = vector_id
                store.upsert(vector_id, vector, {"document_id": doc.id, "chunk_id": chunk.id, "chunk_type": "image"}, "")

            elif doc.doc_type == "pdf":
                pages = extract_pdf_pages(doc.file_path)
                import fitz

                fdoc = fitz.open(doc.file_path)
                pix = fdoc[0].get_pixmap(matrix=fitz.Matrix(0.4, 0.4))
                pix.save(preview_path)
                fdoc.close()

                for page in pages:
                    text = page["text"] or ""
                    if not text.strip():
                        continue
                    chunk = Chunk(document_id=doc.id, chunk_type="pdf_text", ref=str(page["page"]), text_content=text)
                    db.session.add(chunk)
                    db.session.flush()
                    vector_id = f"chunk-{chunk.id}-{uuid.uuid4()}"
                    chunk.vector_id = vector_id
                    vector = embed_text(text[:1000])
                    store.upsert(vector_id, vector, {"document_id": doc.id, "chunk_id": chunk.id, "chunk_type": "pdf_text", "ref": str(page["page"])}, text[:1000])

            elif doc.doc_type == "video":
                extract_poster(doc.file_path, preview_path)
                frame_dir = str(Path(current_app.config["PREVIEW_FOLDER"]) / f"frames_{doc.id}")
                frames = extract_frames(doc.file_path, frame_dir, every_n_seconds=5)
                for frame in frames:
                    chunk = Chunk(document_id=doc.id, chunk_type="video_frame", ref=str(frame["timestamp"]))
                    db.session.add(chunk)
                    db.session.flush()
                    vector_id = f"chunk-{chunk.id}-{uuid.uuid4()}"
                    chunk.vector_id = vector_id
                    vector = embed_image(frame["path"])
                    store.upsert(vector_id, vector, {"document_id": doc.id, "chunk_id": chunk.id, "chunk_type": "video_frame", "ref": str(frame["timestamp"]), "preview_path": frame["path"]}, "")

            doc.preview_path = preview_path
            doc.status = "ready"
            db.session.commit()
            _update_job(job_id, "ready", 100)
        except Exception as exc:  # noqa: BLE001
            doc.status = "failed"
            doc.error_message = str(exc)
            db.session.commit()
            _update_job(job_id, "failed", 100, str(exc))

from __future__ import annotations

import hashlib
import mimetypes
import shutil
import uuid
from pathlib import Path

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from ..models import Chunk, Document, JobStatus, db
from ..services.vector_store import get_vector_store
from ..tasks import enqueue_document_processing

upload_bp = Blueprint("upload", __name__, url_prefix="/api")


def _doc_type_from_mime(mime: str, filename: str) -> str:
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("video/"):
        return "video"
    if mime in {"application/pdf"} or filename.lower().endswith(".pdf"):
        return "pdf"
    raise ValueError("Unsupported file type")


@upload_bp.post("/upload")
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No filename"}), 400

    mime = file.mimetype or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"
    try:
        doc_type = _doc_type_from_mime(mime, file.filename)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    filename = secure_filename(file.filename)
    suffix = Path(filename).suffix
    stored_name = f"{uuid.uuid4()}{suffix}"
    file_path = str(Path(current_app.config["UPLOAD_FOLDER"]) / stored_name)
    file.save(file_path)

    size_bytes = Path(file_path).stat().st_size
    sha256_hash = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()

    doc = Document(
        original_name=filename,
        stored_name=stored_name,
        mime_type=mime,
        doc_type=doc_type,
        file_path=file_path,
        size_bytes=size_bytes,
        status="uploaded",
        sha256_hash=sha256_hash,
    )
    db.session.add(doc)
    db.session.flush()

    job_id = str(uuid.uuid4())
    job = JobStatus(id=job_id, document_id=doc.id, status="queued", progress=0)
    db.session.add(job)
    db.session.commit()

    enqueue_document_processing(current_app._get_current_object(), doc.id, job_id)

    return jsonify({"document_id": doc.id, "job_id": job_id, "status": "queued"}), 202


@upload_bp.get("/jobs/<job_id>")
def get_job(job_id: str):
    job = JobStatus.query.get(job_id)
    if not job:
        return jsonify({"error": "job not found"}), 404
    return jsonify({"status": job.status, "progress": job.progress, "error": job.error})


@upload_bp.get("/documents")
def list_documents():
    docs = Document.query.order_by(Document.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": d.id,
                "name": d.original_name,
                "doc_type": d.doc_type,
                "status": d.status,
                "created_at": d.created_at.isoformat(),
            }
            for d in docs
        ]
    )


@upload_bp.delete("/documents/<int:document_id>")
def delete_document(document_id: int):
    doc = Document.query.get(document_id)
    if not doc:
        return jsonify({"error": "document not found"}), 404

    vector_ids = [c.vector_id for c in doc.chunks if c.vector_id]
    get_vector_store().delete_ids(vector_ids)

    file_path = Path(doc.file_path)
    if file_path.exists():
        file_path.unlink()

    if doc.preview_path:
        preview_path = Path(doc.preview_path)
        if preview_path.exists():
            preview_path.unlink()

    frames_dir = Path(current_app.config["PREVIEW_FOLDER"]) / f"frames_{document_id}"
    if frames_dir.exists() and frames_dir.is_dir():
        shutil.rmtree(frames_dir, ignore_errors=True)

    JobStatus.query.filter_by(document_id=document_id).delete()
    db.session.delete(doc)
    db.session.commit()

    return jsonify({"status": "deleted", "document_id": document_id})

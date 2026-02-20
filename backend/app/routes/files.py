from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, send_file

from ..models import Document

files_bp = Blueprint("files", __name__)


@files_bp.get("/files/<int:document_id>")
def serve_file(document_id: int):
    doc = Document.query.get(document_id)
    if not doc:
        abort(404)
    path = Path(doc.file_path)
    if not path.exists():
        abort(404)
    return send_file(path, mimetype=doc.mime_type, as_attachment=False, download_name=doc.original_name)


@files_bp.get("/files/<int:document_id>/preview")
def serve_preview(document_id: int):
    doc = Document.query.get(document_id)
    if not doc or not doc.preview_path:
        abort(404)
    path = Path(doc.preview_path)
    if not path.exists():
        abort(404)
    return send_file(path, mimetype="image/jpeg")

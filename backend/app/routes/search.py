from __future__ import annotations

from collections import defaultdict

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from ..models import Chunk, Document
from ..services.embed import embed_text
from ..services.vector_store import get_vector_store

search_bp = Blueprint("search", __name__, url_prefix="/api")


def _append_result(results_by_doc: dict, doc: Document, score: float, match: dict) -> None:
    entry = results_by_doc[doc.id]
    entry["document_id"] = doc.id
    entry["doc_type"] = doc.doc_type
    entry["name"] = doc.original_name
    entry["score"] = max(entry.get("score", 0.0), score)
    entry["preview_url"] = f"/files/{doc.id}/preview"
    entry["file_url"] = f"/files/{doc.id}"
    entry.setdefault("face_names", set())
    entry.setdefault("matches", []).append(match)


@search_bp.get("/search")
def search():
    query = request.args.get("q", "").strip()
    doc_type = request.args.get("type")
    limit = int(request.args.get("limit", "20"))
    if not query:
        return jsonify({"query": query, "results": []})

    store = get_vector_store()
    results_by_doc = defaultdict(dict)

    vector = embed_text(query)
    semantic_hits = store.query(vector, limit=limit * 3, where={"chunk_type": {"$in": ["image", "video_frame", "pdf_text"]}})

    ids = semantic_hits.get("ids", [[]])[0]
    metadatas = semantic_hits.get("metadatas", [[]])[0]
    distances = semantic_hits.get("distances", [[]])[0]

    for _id, meta, distance in zip(ids, metadatas, distances):
        _ = _id
        chunk = Chunk.query.get(meta.get("chunk_id"))
        if not chunk:
            continue
        doc = Document.query.get(chunk.document_id)
        if not doc or doc.status != "ready":
            continue
        if doc_type and doc.doc_type != doc_type:
            continue

        score = float(1 - distance)
        _append_result(
            results_by_doc,
            doc,
            score,
            {
                "chunk_type": chunk.chunk_type,
                "ref": chunk.ref,
                "score": round(score, 4),
                "text_snippet": (chunk.text_content or "")[:240],
            },
        )
        if chunk.face_name:
            results_by_doc[doc.id]["face_names"].add(chunk.face_name)

    face_name_rows = (
        Chunk.query.join(Document, Document.id == Chunk.document_id)
        .filter(Document.status == "ready")
        .filter(Chunk.face_name.isnot(None))
        .filter(func.lower(Chunk.face_name).contains(query.lower()))
        .all()
    )

    for chunk in face_name_rows:
        doc = Document.query.get(chunk.document_id)
        if not doc:
            continue
        if doc_type and doc.doc_type != doc_type:
            continue
        _append_result(
            results_by_doc,
            doc,
            1.0,
            {
                "chunk_type": "face_name",
                "ref": chunk.face_name,
                "score": 1.0,
                "text_snippet": f"Matched face tag: {chunk.face_name}",
            },
        )
        results_by_doc[doc.id]["face_names"].add(chunk.face_name)

    results = []
    for _, data in results_by_doc.items():
        face_names = sorted(data.get("face_names", set()))
        data["face_names"] = face_names
        data["score"] = round(data["score"], 4)
        data["matches"] = sorted(data["matches"], key=lambda x: x["score"], reverse=True)[:3]
        results.append(data)

    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"query": query, "results": results[:limit]})


@search_bp.get("/search/similar-faces")
def similar_faces():
    document_id = request.args.get("document_id", type=int)
    limit = int(request.args.get("limit", "12"))
    if not document_id:
        return jsonify({"error": "document_id is required"}), 400

    source = (
        Chunk.query.join(Document, Document.id == Chunk.document_id)
        .filter(Document.id == document_id, Document.status == "ready")
        .filter(Chunk.chunk_type.in_(["image", "video_frame"]))
        .filter(Chunk.vector_id.isnot(None))
        .first()
    )
    if not source:
        return jsonify({"document_id": document_id, "results": []})

    store = get_vector_store()
    payload = store.get_vectors([source.vector_id])
    vectors = payload.get("embeddings") or []
    if not vectors:
        return jsonify({"document_id": document_id, "results": []})

    hits = store.query(vectors[0], limit=limit * 4, where={"chunk_type": {"$in": ["image", "video_frame"]}})

    results_by_doc = defaultdict(dict)
    ids = hits.get("ids", [[]])[0]
    metadatas = hits.get("metadatas", [[]])[0]
    distances = hits.get("distances", [[]])[0]

    for _id, meta, distance in zip(ids, metadatas, distances):
        _ = _id
        chunk = Chunk.query.get(meta.get("chunk_id"))
        if not chunk:
            continue
        if chunk.document_id == document_id:
            continue
        doc = Document.query.get(chunk.document_id)
        if not doc or doc.status != "ready":
            continue

        score = float(1 - distance)
        _append_result(
            results_by_doc,
            doc,
            score,
            {
                "chunk_type": chunk.chunk_type,
                "ref": chunk.ref,
                "score": round(score, 4),
                "text_snippet": (chunk.text_content or "")[:240],
            },
        )
        if chunk.face_name:
            results_by_doc[doc.id]["face_names"].add(chunk.face_name)

    results = []
    for _, data in results_by_doc.items():
        data["face_names"] = sorted(data.get("face_names", set()))
        data["score"] = round(data["score"], 4)
        data["matches"] = sorted(data["matches"], key=lambda x: x["score"], reverse=True)[:3]
        results.append(data)

    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"document_id": document_id, "results": results[:limit]})

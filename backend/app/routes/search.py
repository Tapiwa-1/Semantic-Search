from __future__ import annotations

from collections import defaultdict

from flask import Blueprint, jsonify, request

from ..models import Chunk, Document
from ..services.embed import embed_text
from ..services.vector_store import get_vector_store

search_bp = Blueprint("search", __name__, url_prefix="/api")


@search_bp.get("/search")
def search():
    query = request.args.get("q", "").strip()
    doc_type = request.args.get("type")
    limit = int(request.args.get("limit", "20"))
    if not query:
        return jsonify({"query": query, "results": []})

    vector = embed_text(query)
    store = get_vector_store()
    where = {"chunk_type": {"$in": ["image", "video_frame", "pdf_text"]}}
    if doc_type in {"image", "pdf", "video"}:
        # filter later via SQL record
        pass

    hits = store.query(vector, limit=limit, where=where)
    ids = hits.get("ids", [[]])[0]
    metadatas = hits.get("metadatas", [[]])[0]
    distances = hits.get("distances", [[]])[0]

    grouped = defaultdict(lambda: {"score": 0.0, "matches": []})

    for _id, meta, distance in zip(ids, metadatas, distances):
        chunk = Chunk.query.get(meta.get("chunk_id"))
        if not chunk:
            continue
        doc = Document.query.get(chunk.document_id)
        if not doc or doc.status != "ready":
            continue
        if doc_type and doc.doc_type != doc_type:
            continue

        score = float(1 - distance)
        grouped[doc.id]["score"] = max(grouped[doc.id]["score"], score)
        grouped[doc.id]["matches"].append(
            {
                "chunk_type": chunk.chunk_type,
                "ref": chunk.ref,
                "score": round(score, 4),
                "text_snippet": (chunk.text_content or "")[:240],
            }
        )

    results = []
    for doc_id, data in grouped.items():
        doc = Document.query.get(doc_id)
        results.append(
            {
                "document_id": doc.id,
                "doc_type": doc.doc_type,
                "name": doc.original_name,
                "score": round(data["score"], 4),
                "preview_url": f"/files/{doc.id}/preview",
                "file_url": f"/files/{doc.id}",
                "matches": sorted(data["matches"], key=lambda x: x["score"], reverse=True)[:3],
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify({"query": query, "results": results[:limit]})

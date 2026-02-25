from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection


class VectorStore:
    def __init__(self, persist_path: str):
        Path(persist_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection: Collection = self.client.get_or_create_collection("vault_chunks")

    def upsert(self, vector_id: str, vector: list[float], metadata: dict, document: str = "") -> None:
        self.collection.upsert(ids=[vector_id], embeddings=[vector], metadatas=[metadata], documents=[document])

    def query(self, query_vector: list[float], limit: int = 20, where: dict | None = None) -> dict:
        kwargs = {"query_embeddings": [query_vector], "n_results": limit}
        if where:
            kwargs["where"] = where
        return self.collection.query(**kwargs)

    def get_vectors(self, vector_ids: list[str]) -> dict:
        if not vector_ids:
            return {"ids": [], "embeddings": []}
        return self.collection.get(ids=vector_ids, include=["embeddings", "metadatas"])

    def delete_ids(self, vector_ids: list[str]) -> None:
        if vector_ids:
            self.collection.delete(ids=vector_ids)


def get_vector_store() -> VectorStore:
    return VectorStore(str(Path(__file__).resolve().parent.parent.parent / "chroma"))

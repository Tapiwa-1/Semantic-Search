from __future__ import annotations

from functools import lru_cache

from PIL import Image
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer("clip-ViT-B-32")


def embed_text(text: str) -> list[float]:
    model = get_model()
    return model.encode([text], normalize_embeddings=True)[0].tolist()


def embed_image(path: str) -> list[float]:
    model = get_model()
    image = Image.open(path).convert("RGB")
    return model.encode([image], normalize_embeddings=True)[0].tolist()

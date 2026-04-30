from __future__ import annotations

import os
from functools import lru_cache

from typing import Any

try:
    # Heavy dependency; imported lazily via get_embedder().
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore

EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))
DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_embedder() -> Any:
    if SentenceTransformer is None:
        raise RuntimeError(
            "sentence-transformers is not installed. Add it to dependencies (pyproject.toml) "
            "and reinstall your environment."
        )

    # Lazily load once per process.
    model_name = DEFAULT_MODEL
    model = SentenceTransformer(model_name)
    return model


def embed_text(text: str) -> list[float]:
    """
    Return an embedding vector for `text`.

    Note: cosine similarity is computed by pgvector at query time; we store the raw embedding.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        # Keep vector dimensionality stable for easier downstream handling.
        return [0.0] * EMBEDDING_DIM

    embedder = get_embedder()
    # sentence-transformers returns numpy array; convert to python floats for SQLAlchemy binding.
    vec = embedder.encode([cleaned])[0]

    floats = [float(x) for x in vec]
    if len(floats) != EMBEDDING_DIM:
        # Fail fast rather than inserting wrong-size vectors.
        raise ValueError(
            f"Embedding dimension mismatch: expected {EMBEDDING_DIM}, got {len(floats)} "
            f"(model={DEFAULT_MODEL}). Set EMBEDDING_DIM accordingly."
        )
    return floats


"""
Embedding Generator (Module 3)

Why embeddings:
- We convert text chunks into dense vectors so we can do similarity search.
- Vector similarity lets us retrieve the most relevant knowledge snippets for a user query.

This uses only free/open-source tools:
- sentence-transformers (e.g. all-MiniLM-L6-v2)

Notes:
- We normalize embeddings so cosine similarity == inner product on normalized vectors.
- Keep embedding logic separate from storage logic (vector_store.py).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class EmbedderConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    normalize: bool = True


class Embedder:
    def __init__(self, config: EmbedderConfig | None = None):
        self.config = config or EmbedderConfig()
        # Try local files first to avoid blocking on network
        try:
            # First try with local files only (fast, no network)
            self.model = SentenceTransformer(self.config.model_name, local_files_only=True)
        except Exception:
            # If local files don't work, try without local_files_only (may block)
            # But set a timeout or catch quickly
            try:
                self.model = SentenceTransformer(self.config.model_name)
            except Exception as e:
                print(f"Warning: Could not load model {self.config.model_name}: {type(e).__name__}")
                print("Using fallback embedding method (zero vectors). Some features may be limited.")
                self.model = None

    @property
    def embedding_dim(self) -> int:
        # sentence-transformers exposes this on the model
        if self.model is None:
            return 384  # Default dimension for all-MiniLM-L6-v2
        return int(self.model.get_sentence_embedding_dimension())

    def embed_texts(self, texts: Sequence[str]) -> np.ndarray:
        """
        Embed a list of strings into a float32 numpy array: (N, D).
        """
        texts_list: List[str] = [t or "" for t in texts]
        if len(texts_list) == 0:
            return np.zeros((0, self.embedding_dim), dtype=np.float32)

        if self.model is None:
            # Fallback: return zero vectors (will result in no matches, but won't crash)
            return np.zeros((len(texts_list), self.embedding_dim), dtype=np.float32)

        try:
            emb = self.model.encode(
                texts_list,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=self.config.normalize,
            )
            # Ensure float32 for FAISS
            return np.asarray(emb, dtype=np.float32)
        except Exception as e:
            print(f"Warning: Embedding failed: {e}. Returning zero vectors.")
            return np.zeros((len(texts_list), self.embedding_dim), dtype=np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string into shape (D,).
        """
        vec = self.embed_texts([query])
        return vec[0]


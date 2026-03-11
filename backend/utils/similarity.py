"""
Similarity utilities for Module 4 (Skill Gap Analysis).

Why semantic similarity instead of exact match?
- Job descriptions and resumes rarely use *exactly* the same wording.
- Embeddings + cosine similarity let us see when two skills are *meaning-wise* close
  (e.g. "PyTorch" vs "Deep learning with PyTorch").

These helpers operate on numpy arrays and make no network calls.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np


def cosine_similarity_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between two batches of vectors.

    Args:
        a: Array of shape (N, D)
        b: Array of shape (M, D)

    Returns:
        sim: Array of shape (N, M) where sim[i, j] = cosine(a[i], b[j])

    Note:
        Our Embedder already returns L2-normalized vectors, but we normalize again
        defensively so this utility is safe to use with any embeddings.
    """
    if a.size == 0 or b.size == 0:
        return np.zeros((a.shape[0], b.shape[0]), dtype=np.float32)

    # Convert to float32 and ensure 2D
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)

    # L2-normalize rows
    def _norm(x: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(x, axis=1, keepdims=True) + 1e-8
        return x / norms

    a_n = _norm(a)
    b_n = _norm(b)

    return a_n @ b_n.T


def max_similarities(
    a: np.ndarray,
    b: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    For each vector in a, find the maximum cosine similarity against any vector in b.

    Args:
        a: Array of shape (N, D)
        b: Array of shape (M, D)

    Returns:
        max_scores: shape (N,) – best score for each row in a
        argmax_idx: shape (N,) – index into b for best match (-1 if b is empty)
    """
    if b.size == 0:
        return np.zeros((a.shape[0],), dtype=np.float32), -np.ones((a.shape[0],), dtype=np.int64)

    sim = cosine_similarity_matrix(a, b)  # (N, M)
    argmax_idx = np.argmax(sim, axis=1)
    max_scores = sim[np.arange(sim.shape[0]), argmax_idx]
    return max_scores, argmax_idx


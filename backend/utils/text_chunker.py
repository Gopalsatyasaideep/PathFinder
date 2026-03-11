"""
Text Chunking Utilities (Module 3)

Why chunking is needed:
- Embedding models have an input length limit. Large documents (full resumes, long job posts)
  must be split into smaller pieces.
- Smaller chunks improve retrieval precision: vector search can return the most relevant part
  of a document instead of the entire document.

This chunker is intentionally simple and dependency-light:
- It chunks by "word tokens" (rough proxy for model tokens).
- It adds overlap to preserve context across chunk boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class TextChunk:
    """A chunk of text with basic offsets for debugging/traceability."""

    content: str
    start_word: int
    end_word: int


def _normalize_text(text: str) -> str:
    text = text or ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WHITESPACE_RE.sub(" ", text).strip()
    return text


def chunk_text(
    text: str,
    *,
    chunk_size: int = 300,
    chunk_overlap: int = 60,
) -> List[TextChunk]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text
        chunk_size: Approx "token" count (here: words) per chunk. Recommended 200–500.
        chunk_overlap: Overlap between consecutive chunks to preserve context.

    Returns:
        List of TextChunk objects.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be < chunk_size")

    text = _normalize_text(text)
    if not text:
        return []

    words = text.split(" ")
    n = len(words)

    chunks: List[TextChunk] = []
    start = 0
    step = chunk_size - chunk_overlap

    while start < n:
        end = min(n, start + chunk_size)
        content = " ".join(words[start:end]).strip()
        if content:
            chunks.append(TextChunk(content=content, start_word=start, end_word=end))
        if end == n:
            break
        start += step

    return chunks


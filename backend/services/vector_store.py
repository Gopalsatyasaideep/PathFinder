"""
Vector Store (FAISS) - Module 3

What this module provides:
- Build a knowledge base of chunked documents (resume text, job descriptions, skill requirements, learning resources)
- Embed chunks using sentence-transformers
- Store embeddings in a local FAISS index (open-source, free)
- Retrieve top-k relevant chunks for a query (similarity search) along with metadata
- Save/load the index to disk to persist across server restarts

Why vector search:
- Instead of keyword matching, embeddings capture meaning (semantic similarity).
- This improves retrieval for varied phrasing (important for RAG).
"""

from __future__ import annotations

import json
import os
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import faiss  # type: ignore
import numpy as np

from embeddings.embedder import Embedder, EmbedderConfig
from utils.text_chunker import TextChunk, chunk_text


@dataclass
class ChunkMetadata:
    source_type: str  # "resume" | "job" | "skills" | "learning"
    document_id: str
    tag: Optional[str] = None  # e.g. "data_engineering", "frontend", etc.
    chunk_index: int = 0


@dataclass
class RetrievedChunk:
    content: str
    metadata: ChunkMetadata
    score: float


class FaissVectorStore:
    """
    A minimal FAISS-backed vector store with:
    - incremental additions
    - persistence (index + metadata/texts)
    - cosine similarity (via normalized embeddings + inner product index)
    """

    def __init__(
        self,
        *,
        persist_dir: str | Path = Path("vector_store"),
        embedder_config: EmbedderConfig | None = None,
    ):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self._embedder_config = embedder_config
        self._embedder: Optional[Embedder] = None
        # Default dimension for all-MiniLM-L6-v2
        self.dim = 384

        # Use inner product index. With normalized vectors, this is cosine similarity.
        self.index: faiss.Index = faiss.IndexFlatIP(self.dim)

        # Aligned storage (row i corresponds to vector i in FAISS)
        self.texts: List[str] = []
        self.metadatas: List[ChunkMetadata] = []

        self._index_path = self.persist_dir / "faiss.index"
        self._payload_path = self.persist_dir / "payload.pkl"

        # Auto-load if present
        if self._index_path.exists() and self._payload_path.exists():
            try:
                self.load()
            except Exception:
                # If load fails, start fresh
                pass
    
    @property
    def embedder(self) -> Embedder:
        """Lazy initialization of embedder."""
        if self._embedder is None:
            try:
                self._embedder = Embedder(self._embedder_config)
                self.dim = self._embedder.embedding_dim
                if hasattr(self.index, 'd') and self.index.d != self.dim:
                    self.index = faiss.IndexFlatIP(self.dim)
            except Exception as e:
                # Create a fallback embedder that returns zero vectors
                print(f"Warning: Using fallback embedder: {type(e).__name__}")
                class DummyEmbedder:
                    def __init__(self):
                        self.embedding_dim = 384
                    def embed_texts(self, texts):
                        import numpy as np
                        return np.zeros((len(texts), 384), dtype=np.float32)
                self._embedder = DummyEmbedder()
        return self._embedder

    def __len__(self) -> int:
        return len(self.texts)

    def add_document(
        self,
        *,
        source_type: str,
        document_id: str,
        text: str,
        tag: Optional[str] = None,
        chunk_size: int = 300,
        chunk_overlap: int = 60,
    ) -> int:
        """
        Chunk + embed + add to FAISS with metadata. Returns number of chunks added.
        """
        chunks: List[TextChunk] = chunk_text(text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if not chunks:
            return 0

        contents = [c.content for c in chunks]
        vectors = self.embedder.embed_texts(contents)  # (N, D) float32

        start_idx = len(self.texts)
        self.index.add(vectors)

        for i, c in enumerate(chunks):
            self.texts.append(c.content)
            self.metadatas.append(
                ChunkMetadata(
                    source_type=source_type,
                    document_id=document_id,
                    tag=tag,
                    chunk_index=i,
                )
            )

        return len(chunks)

    def add_documents_bulk(
        self,
        docs: Sequence[Tuple[str, str, str, Optional[str]]],
        *,
        chunk_size: int = 300,
        chunk_overlap: int = 60,
    ) -> int:
        """
        Add many documents efficiently.

        docs: sequence of (source_type, document_id, text, tag)
        """
        total = 0
        for source_type, doc_id, text, tag in docs:
            total += self.add_document(
                source_type=source_type,
                document_id=doc_id,
                text=text,
                tag=tag,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )
        return total

    def save(self) -> None:
        """
        Save FAISS index + payload to disk.
        """
        faiss.write_index(self.index, str(self._index_path))
        with open(self._payload_path, "wb") as f:
            pickle.dump(
                {
                    "dim": self.dim,
                    "texts": self.texts,
                    "metadatas": self.metadatas,
                },
                f,
            )

    def load(self) -> None:
        """
        Load FAISS index + payload from disk.
        """
        self.index = faiss.read_index(str(self._index_path))
        with open(self._payload_path, "rb") as f:
            payload = pickle.load(f)

        if int(payload.get("dim", -1)) != self.dim:
            raise ValueError(
                f"Embedding dimension mismatch. Stored={payload.get('dim')} Current={self.dim}. "
                "Delete the persisted vector_store folder and rebuild."
            )

        self.texts = list(payload["texts"])
        self.metadatas = list(payload["metadatas"])

    def search(self, query: str, *, top_k: int = 5) -> Dict[str, Any]:
        """
        Retrieve top-k relevant chunks for a query.

        Returns a JSON-serializable dict matching the requested example shape.
        """
        if len(self) == 0:
            return {"query": query, "results": []}

        try:
            # Try to get embedder, but if it fails quickly, return empty
            embedder = self.embedder
            q = embedder.embed_texts([query])  # (1, D)
            # Check if we got valid embeddings (not all zeros)
            if q is None or (q.size > 0 and np.all(q == 0)):
                # Embedder failed or returned zeros, return empty results
                return {"query": query, "results": []}
            
            scores, indices = self.index.search(q, top_k)

            results: List[Dict[str, Any]] = []
            for score, idx in zip(scores[0].tolist(), indices[0].tolist()):
                if idx < 0 or idx >= len(self.texts):
                    continue
                md = self.metadatas[idx]
                results.append(
                    {
                        "content": self.texts[idx],
                        "source": md.source_type,
                        "score": float(score),
                        "metadata": asdict(md),
                    }
                )

            return {"query": query, "results": results}
        except (TimeoutError, Exception) as e:
            # If search fails (including timeout), return empty results immediately
            return {"query": query, "results": []}

    # ---------- Simple ingestion helpers (files/folders) ----------

    def ingest_directory(
        self,
        *,
        source_type: str,
        directory: str | Path,
        tag: Optional[str] = None,
        file_extensions: Tuple[str, ...] = (".txt", ".md", ".json"),
        chunk_size: int = 300,
        chunk_overlap: int = 60,
    ) -> int:
        """
        Ingest all files in a directory.
        - .txt/.md are read as plain text
        - .json: if it's a dict or list, we stringify it for embedding (simple + robust)
        """
        directory = Path(directory)
        if not directory.exists():
            return 0

        total = 0
        for p in sorted(directory.rglob("*")):
            if not p.is_file():
                continue
            if p.suffix.lower() not in file_extensions:
                continue

            try:
                if p.suffix.lower() == ".json":
                    obj = json.loads(p.read_text(encoding="utf-8", errors="ignore") or "{}")
                    text = json.dumps(obj, ensure_ascii=False, indent=2)
                else:
                    text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            doc_id = str(p.relative_to(directory))
            total += self.add_document(
                source_type=source_type,
                document_id=doc_id,
                text=text,
                tag=tag,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

        return total


def build_default_kb(persist_dir: str | Path = Path("vector_store")) -> FaissVectorStore:
    """
    Build (or load) a KB from the default backend/data folders.
    This is a convenient entry point for later RAG modules.
    """
    store = FaissVectorStore(persist_dir=persist_dir)

    base = Path(__file__).resolve().parents[1] / "data"
    # You can drop files into these folders:
    store.ingest_directory(source_type="job", directory=base / "jobs", tag="jobs")
    store.ingest_directory(source_type="skills", directory=base / "skills", tag="skills")
    store.ingest_directory(source_type="learning", directory=base / "learning_resources", tag="learning")

    store.save()
    return store


if __name__ == "__main__":
    # Simple CLI test (optional):
    # 1) Put some .txt/.md/.json files into backend/data/jobs, backend/data/skills, backend/data/learning_resources
    # 2) Run: py services/vector_store.py
    # 3) Type queries and see retrieved chunks.
    store = build_default_kb(persist_dir=Path("vector_store"))
    print(f"KB ready. Total chunks: {len(store)}")
    while True:
        q = input("\nQuery (or 'exit'): ").strip()
        if not q or q.lower() == "exit":
            break
        print(json.dumps(store.search(q, top_k=5), indent=2, ensure_ascii=False))


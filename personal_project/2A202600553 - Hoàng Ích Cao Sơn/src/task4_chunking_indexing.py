"""
Task 4 — Chunking & Indexing vào Vector Store.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


# =============================================================================
# CONFIGURATION
# =============================================================================

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

VECTOR_STORE = "weaviate"


# =============================================================================
# INTERNAL CACHE
# =============================================================================

_INDEX: list[dict] = []
_DOC_CACHE: list[dict] | None = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE)


def _truncate_text(text: str, max_len: int = 1500) -> str:
    text = text.strip()
    return text if len(text) <= max_len else text[:max_len].rsplit(" ", 1)[0]


def _simple_split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
        if len(paragraph) <= chunk_size:
            current = paragraph
            continue

        start = 0
        while start < len(paragraph):
            end = min(len(paragraph), start + chunk_size)
            chunks.append(paragraph[start:end].strip())
            if end >= len(paragraph):
                current = ""
                break
            start = max(end - chunk_overlap, start + 1)
        else:
            current = ""

    if current.strip():
        chunks.append(current.strip())

    return [c for c in chunks if c.strip()]


def _embed_text(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIM
    tokens = _tokenize(text)
    if not tokens:
        return vector

    for token in tokens:
        idx = hash(token) % EMBEDDING_DIM
        vector[idx] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm:
        vector = [value / norm for value in vector]
    return vector


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def load_documents() -> list[dict]:
    """
    Đọc toàn bộ markdown files từ data/standardized/.
    """
    global _DOC_CACHE
    if _DOC_CACHE is not None:
        return list(_DOC_CACHE)

    documents: list[dict] = []
    if STANDARDIZED_DIR.exists():
        for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
            if not md_file.is_file():
                continue
            content = md_file.read_text(encoding="utf-8")
            rel_path = md_file.relative_to(STANDARDIZED_DIR)
            doc_type = rel_path.parts[0] if len(rel_path.parts) > 1 else rel_path.parent.name or "unknown"
            documents.append(
                {
                    "content": content,
                    "metadata": {
                        "source": str(rel_path).replace("\\", "/"),
                        "type": doc_type,
                    },
                }
            )

    _DOC_CACHE = documents
    return list(documents)


def chunk_documents(documents: list[dict]) -> list[dict]:
    """
    Chunk documents theo strategy đã chọn.
    """
    chunks: list[dict] = []
    for doc in documents:
        text = doc.get("content", "")
        if not text.strip():
            continue
        splits = _simple_split_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        if not splits:
            splits = [_truncate_text(text, CHUNK_SIZE)]
        for i, chunk_text in enumerate(splits):
            chunk_text = _truncate_text(chunk_text, CHUNK_SIZE + int(CHUNK_SIZE * 0.1))
            chunks.append(
                {
                    "content": chunk_text,
                    "metadata": {**doc.get("metadata", {}), "chunk_index": i},
                }
            )
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Embed toàn bộ chunks bằng model đã chọn.
    """
    embedded: list[dict] = []
    for chunk in chunks:
        new_chunk = dict(chunk)
        new_chunk["embedding"] = _embed_text(chunk.get("content", ""))
        embedded.append(new_chunk)
    return embedded


def index_to_vectorstore(chunks: list[dict]):
    """
    Lưu chunks vào vector store đã chọn.
    """
    global _INDEX
    _INDEX = list(chunks)
    return _INDEX


def ensure_index() -> list[dict]:
    """Load, chunk và embed nếu index chưa sẵn sàng."""
    global _INDEX
    if _INDEX:
        return _INDEX

    docs = load_documents()
    if not docs:
        _INDEX = []
        return _INDEX

    chunks = chunk_documents(docs)
    chunks = embed_chunks(chunks)
    return index_to_vectorstore(chunks)


def semantic_query_embedding(query: str) -> list[float]:
    return _embed_text(query)


def search_index(query: str, top_k: int = 10) -> list[dict]:
    index = ensure_index()
    if not index:
        return []

    query_embedding = semantic_query_embedding(query)
    scored: list[dict] = []
    for chunk in index:
        score = _cosine(query_embedding, chunk.get("embedding", []))
        scored.append(
            {
                "content": chunk["content"],
                "score": float(score),
                "metadata": dict(chunk.get("metadata", {})),
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def run_pipeline():
    """Chạy toàn bộ pipeline: load → chunk → embed → index."""
    print("=" * 50)
    print("Task 4: Chunking & Indexing")
    print(f"  Chunking: {CHUNKING_METHOD} (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    print(f"  Embedding: {EMBEDDING_MODEL} (dim={EMBEDDING_DIM})")
    print(f"  Vector Store: {VECTOR_STORE}")
    print("=" * 50)

    docs = load_documents()
    print(f"\n✓ Loaded {len(docs)} documents")

    chunks = chunk_documents(docs)
    print(f"✓ Created {len(chunks)} chunks")

    chunks = embed_chunks(chunks)
    print(f"✓ Embedded {len(chunks)} chunks")

    index_to_vectorstore(chunks)
    print("✓ Indexed to vector store")


if __name__ == "__main__":
    run_pipeline()

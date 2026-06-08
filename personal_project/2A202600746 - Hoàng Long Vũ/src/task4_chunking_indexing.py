"""Task 4: load Markdown documents, chunk them, and expose an in-memory index."""

from __future__ import annotations

import hashlib
import math
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"

# Recursive character chunking is robust for mixed legal/news Markdown.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive_character"

# The exercise runs offline, so this module uses deterministic hashed TF vectors.
EMBEDDING_MODEL = "local-hashed-tfidf"
EMBEDDING_DIM = 256
VECTOR_STORE = "in_memory"


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w]+", normalize_text(text), flags=re.UNICODE)


def load_documents() -> list[dict]:
    """Read all Markdown files from data/standardized."""
    documents: list[dict] = []
    for md_file in sorted(STANDARDIZED_DIR.rglob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        if not content.strip():
            continue
        doc_type = "legal" if "legal" in md_file.parts else "news"
        documents.append(
            {
                "content": content,
                "metadata": {
                    "source": md_file.name,
                    "path": str(md_file.relative_to(STANDARDIZED_DIR)),
                    "type": doc_type,
                },
            }
        )
    return documents


def _split_text(text: str) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chunk documents into overlapping character windows."""
    chunks: list[dict] = []
    for doc in documents:
        for i, chunk_text in enumerate(_split_text(doc["content"])):
            chunks.append(
                {
                    "content": chunk_text,
                    "metadata": {**doc.get("metadata", {}), "chunk_index": i},
                }
            )
    return chunks


def _hash_token(token: str) -> int:
    digest = hashlib.md5(token.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % EMBEDDING_DIM


def embed_text(text: str) -> list[float]:
    vector = [0.0] * EMBEDDING_DIM
    for token in tokenize(text):
        vector[_hash_token(token)] += 1.0
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def embed_chunks(chunks: list[dict]) -> list[dict]:
    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["content"])
    return chunks


@lru_cache(maxsize=1)
def get_index() -> tuple[dict, ...]:
    docs = load_documents()
    chunks = embed_chunks(chunk_documents(docs))
    return tuple(chunks)


def index_to_vectorstore(chunks: list[dict]) -> tuple[dict, ...]:
    """Return an in-memory vector store compatible with the search modules."""
    return tuple(chunks)


def run_pipeline() -> tuple[dict, ...]:
    return get_index()


if __name__ == "__main__":
    index = run_pipeline()
    print(f"Indexed {len(index)} chunks with {EMBEDDING_MODEL}.")

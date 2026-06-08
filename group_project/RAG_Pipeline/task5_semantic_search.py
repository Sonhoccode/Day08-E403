"""
Task 5 — Semantic Search Module.

Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""
import re
from pathlib import Path

try:
    import chromadb
except Exception:  # pragma: no cover
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None

db_path = Path(__file__).parent.parent / "data" / "chroma_db"
repo_root = Path(__file__).resolve().parents[2]
client = chromadb.PersistentClient(path=str(db_path)) if chromadb else None
try:
    collection = client.get_collection("DrugLawDocs") if client else None
except Exception:
    collection = None


class _FallbackEncoder:
    def encode(self, text: str):
        tokens = _tokenize(text)
        vec = [0.0] * 384
        for token in tokens:
            vec[hash(token) % len(vec)] += 1.0
        return vec


model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2") if SentenceTransformer else _FallbackEncoder()

_FALLBACK_DOCS: list[dict] | None = None
_FALLBACK_EMBEDDINGS: list[list[float]] | None = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE)


def _load_fallback_docs() -> list[dict]:
    global _FALLBACK_DOCS
    if _FALLBACK_DOCS is not None:
        return _FALLBACK_DOCS

    docs: list[dict] = []
    search_roots = [repo_root / "group_project" / "data" / "standardized"]
    search_roots.extend(repo_root.glob("personal_project/**/data/standardized"))

    seen_paths: set[Path] = set()
    for root in search_roots:
        if not root.exists():
            continue
        for md_file in root.rglob("*.md"):
            if md_file in seen_paths or not md_file.is_file():
                continue
            seen_paths.add(md_file)
            docs.append(
                {
                    "content": md_file.read_text(encoding="utf-8"),
                    "metadata": {
                        "source": str(md_file.relative_to(root)).replace("\\", "/"),
                        "type": md_file.parent.name,
                    },
                }
            )

    _FALLBACK_DOCS = docs
    return docs


def _ensure_fallback_embeddings() -> list[list[float]]:
    global _FALLBACK_EMBEDDINGS
    if _FALLBACK_EMBEDDINGS is not None:
        return _FALLBACK_EMBEDDINGS

    docs = _load_fallback_docs()
    embeddings = []
    for doc in docs:
        emb = model.encode(doc["content"])
        if hasattr(emb, "tolist"):
            emb = emb.tolist()
        embeddings.append(emb)
    _FALLBACK_EMBEDDINGS = embeddings
    return _FALLBACK_EMBEDDINGS


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if not norm_a or not norm_b:
        return 0.0
    return float(dot / (norm_a * norm_b))


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    query_embedding = model.encode(query)
    if hasattr(query_embedding, "tolist"):
        query_embedding = query_embedding.tolist()

    if collection:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        output = []
        if not results["ids"] or not results["ids"][0]:
            return output
            
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            output.append({
                "content": doc,
                "score": 1.0 - float(dist), # cosine distance -> similarity
                "metadata": meta
            })
        return output

    docs = _load_fallback_docs()
    if not docs:
        return []

    embeddings = _ensure_fallback_embeddings()
    scored = []
    for doc, emb in zip(docs, embeddings):
        scored.append(
            {
                "content": doc["content"],
                "score": _cosine(query_embedding, emb),
                "metadata": doc["metadata"],
            }
        )
    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    # Test
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")

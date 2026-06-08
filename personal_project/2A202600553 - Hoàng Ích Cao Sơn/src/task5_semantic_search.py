"""
Task 5 — Semantic Search Module.
"""

from __future__ import annotations

from .task4_chunking_indexing import ensure_index, semantic_query_embedding


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    return sum(x * y for x, y in zip(a, b))


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.
    """
    index = ensure_index()
    if not index:
        return []

    query_embedding = semantic_query_embedding(query)
    results: list[dict] = []
    for chunk in index:
        score = _cosine(query_embedding, chunk.get("embedding", []))
        results.append(
            {
                "content": chunk["content"],
                "score": float(score),
                "metadata": dict(chunk.get("metadata", {})),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")

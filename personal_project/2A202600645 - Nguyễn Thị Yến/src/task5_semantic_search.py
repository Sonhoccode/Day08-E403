"""
Task 5 — Semantic Search Module.
Viết module tìm kiếm ngữ nghĩa (dense retrieval) trên vector store.

Yêu cầu:
    - Input: query string + top_k
    - Output: danh sách chunks có score, sorted descending
    - Phải tương thích với embedding model và vector store ở Task 4
"""

import math

from .task4_chunking_indexing import embed_chunks, load_or_build_index


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
    if not query.strip() or top_k <= 0:
        return []
    query_vector = embed_chunks([{"content": query, "metadata": {}}])[0]["embedding"]
    results = []
    for chunk in load_or_build_index():
        embedding = chunk.get("embedding", [])
        score = sum(a * b for a, b in zip(query_vector, embedding))
        if math.isfinite(score) and score > 0:
            results.append({
                "content": chunk["content"],
                "score": float(score),
                "metadata": chunk.get("metadata", {}),
            })
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    # Test
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")

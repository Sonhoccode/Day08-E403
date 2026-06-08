"""Task 5: semantic search over the local in-memory vector index."""

from .task4_chunking_indexing import cosine_similarity, embed_text, get_index


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    query_embedding = embed_text(query)
    results: list[dict] = []
    for chunk in get_index():
        score = cosine_similarity(query_embedding, chunk["embedding"])
        if score <= 0:
            continue
        results.append(
            {
                "content": chunk["content"],
                "score": float(score),
                "metadata": dict(chunk.get("metadata", {})),
            }
        )
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in semantic_search("hinh phat tang tru ma tuy", top_k=5):
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")

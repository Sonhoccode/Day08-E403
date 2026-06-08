"""Task 7: lightweight reranking implementations."""

from .task4_chunking_indexing import cosine_similarity, embed_text, tokenize


def rerank_cross_encoder(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    """Offline lexical/semantic relevance scorer used as a cross-encoder stand-in."""
    query_tokens = set(tokenize(query))
    query_embedding = embed_text(query)
    reranked: list[dict] = []
    for candidate in candidates:
        content = candidate.get("content", "")
        content_tokens = set(tokenize(content))
        overlap = len(query_tokens & content_tokens) / max(len(query_tokens), 1)
        semantic = cosine_similarity(query_embedding, embed_text(content))
        original = float(candidate.get("score", 0.0))
        score = 0.55 * semantic + 0.35 * overlap + 0.10 * original
        item = dict(candidate)
        item["score"] = float(score)
        reranked.append(item)
    return sorted(reranked, key=lambda item: item["score"], reverse=True)[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    selected: list[int] = []
    remaining = list(range(len(candidates)))
    embeddings = [item.get("embedding") or embed_text(item.get("content", "")) for item in candidates]

    while remaining and len(selected) < top_k:
        best_idx = remaining[0]
        best_score = float("-inf")
        for idx in remaining:
            relevance = cosine_similarity(query_embedding, embeddings[idx])
            diversity_penalty = max(
                (cosine_similarity(embeddings[idx], embeddings[sel]) for sel in selected),
                default=0.0,
            )
            score = lambda_param * relevance - (1 - lambda_param) * diversity_penalty
            if score > best_score:
                best_score = score
                best_idx = idx
        item = dict(candidates[best_idx])
        item["score"] = float(best_score)
        candidates[best_idx] = item
        selected.append(best_idx)
        remaining.remove(best_idx)

    return [candidates[i] for i in selected]


def rerank_rrf(ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60) -> list[dict]:
    scores: dict[str, float] = {}
    items: dict[str, dict] = {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item.get("metadata", {}).get("path") or item["content"]
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            items[key] = item

    results = []
    for key, score in sorted(scores.items(), key=lambda pair: pair[1], reverse=True)[:top_k]:
        item = dict(items[key])
        item["score"] = float(score)
        results.append(item)
    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",
) -> list[dict]:
    if not candidates:
        return []
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    if method == "mmr":
        return rerank_mmr(embed_text(query), candidates, top_k)
    if method == "rrf":
        return rerank_rrf([candidates], top_k)
    raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    demo = [
        {"content": "Dieu 249 toi tang tru trai phep chat ma tuy", "score": 0.8, "metadata": {}},
        {"content": "Python programming", "score": 0.4, "metadata": {}},
    ]
    print(rerank("hinh phat ma tuy", demo, top_k=2))

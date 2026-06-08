"""
Task 7 — Reranking Module.
"""

from __future__ import annotations

from typing import Optional


def _tokenize(text: str) -> set[str]:
    import re

    return set(re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE))


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank candidates sử dụng heuristic cross-encoder local fallback.
    """
    query_tokens = _tokenize(query)
    ranked: list[dict] = []

    for candidate in candidates:
        content = candidate.get("content", "")
        content_tokens = _tokenize(content)
        overlap = len(query_tokens & content_tokens)
        coverage = overlap / max(len(query_tokens), 1)
        base_score = float(candidate.get("score", 0.0))
        rerank_score = base_score + (coverage * 2.0) + (overlap * 0.1)
        item = dict(candidate)
        item["score"] = float(rerank_score)
        item["rerank_score"] = float(rerank_score)
        ranked.append(item)

    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance.
    """
    def cosine(a: list[float], b: list[float]) -> float:
        if not a or not b:
            return 0.0
        return sum(x * y for x, y in zip(a, b))

    selected: list[int] = []
    remaining = list(range(len(candidates)))

    for _ in range(min(top_k, len(candidates))):
        best_idx: Optional[int] = None
        best_score = float("-inf")

        for idx in remaining:
            relevance = cosine(query_embedding, candidates[idx].get("embedding", []))
            max_sim_to_selected = 0.0
            for sel_idx in selected:
                sim = cosine(candidates[idx].get("embedding", []), candidates[sel_idx].get("embedding", []))
                max_sim_to_selected = max(max_sim_to_selected, sim)
            mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx

        if best_idx is None:
            break
        selected.append(best_idx)
        remaining.remove(best_idx)

    return [dict(candidates[i]) | {"score": float(candidates[i].get("score", 0.0))} for i in selected]


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion.
    """
    rrf_scores: dict[str, float] = {}
    content_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item.get("content", "")
            if not key:
                continue
            rrf_scores[key] = rrf_scores.get(key, 0.0) + 1 / (k + rank)
            content_map[key] = dict(item)

    sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    results: list[dict] = []
    for content, score in sorted_items[:top_k]:
        item = dict(content_map[content])
        item["score"] = float(score)
        results.append(item)
    return results


def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",
) -> list[dict]:
    """
    Unified reranking interface.
    """
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
        raise NotImplementedError("Call rerank_mmr with query_embedding")
    elif method == "rrf":
        raise NotImplementedError("Call rerank_rrf with ranked_lists")
    else:
        raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    dummy_candidates = [
        {"content": "Điều 248: Tội tàng trữ trái phép chất ma tuý", "score": 0.8, "metadata": {}},
        {"content": "Nghệ sĩ X bị bắt vì sử dụng ma tuý", "score": 0.7, "metadata": {}},
        {"content": "Hình phạt tù từ 2-7 năm cho tội tàng trữ", "score": 0.6, "metadata": {}},
    ]
    results = rerank("hình phạt tàng trữ ma tuý", dummy_candidates, top_k=2)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content']}")

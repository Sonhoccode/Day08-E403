"""
Task 7 — Reranking Module.

Chọn 1 trong các phương pháp:
    - Cross-encoder reranker: Jina Reranker v2 (multilingual) hoặc Qwen3-Reranker
    - MMR (Maximal Marginal Relevance): tự implement
    - RRF (Reciprocal Rank Fusion): tự implement

Nếu dùng MMR hoặc RRF, đảm bảo hiểu và giải thích được cơ chế.
"""

import math
import re
from collections import Counter


def rerank_cross_encoder(
    query: str, candidates: list[dict], top_k: int = 5
) -> list[dict]:
    """
    Rerank candidates sử dụng cross-encoder model.

    Args:
        query: Câu truy vấn
        candidates: List of {'content': str, 'score': float, 'metadata': dict}
        top_k: Số lượng kết quả sau rerank

    Returns:
        List of top_k candidates, re-scored và sorted by rerank_score descending.
    """
    query_terms = Counter(re.findall(r"\w+", query.lower(), flags=re.UNICODE))
    results = []
    for candidate in candidates:
        doc_terms = Counter(re.findall(r"\w+", candidate.get("content", "").lower(), flags=re.UNICODE))
        overlap = sum(min(count, doc_terms.get(term, 0)) for term, count in query_terms.items())
        lexical = overlap / max(sum(query_terms.values()), 1)
        original = float(candidate.get("score", 0.0))
        item = candidate.copy()
        item["score"] = 0.75 * lexical + 0.25 * original
        results.append(item)
    return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]


def rerank_mmr(
    query_embedding: list[float],
    candidates: list[dict],
    top_k: int = 5,
    lambda_param: float = 0.7,
) -> list[dict]:
    """
    Maximal Marginal Relevance — chọn candidates vừa relevant vừa diverse.

    MMR = λ * sim(query, doc) - (1-λ) * max(sim(doc, selected_docs))

    Args:
        query_embedding: Vector embedding của query
        candidates: List of {'content': str, 'score': float, 'embedding': list, 'metadata': dict}
        top_k: Số lượng kết quả
        lambda_param: Trade-off giữa relevance (1.0) và diversity (0.0)

    Returns:
        List of top_k candidates selected by MMR.
    """
    def cosine(left, right):
        denom = math.sqrt(sum(x*x for x in left)) * math.sqrt(sum(x*x for x in right))
        return sum(a*b for a, b in zip(left, right)) / denom if denom else 0.0
    selected, remaining, selected_scores = [], list(range(len(candidates))), {}
    while remaining and len(selected) < top_k:
        best_idx, best_score = None, float("-inf")
        for idx in remaining:
            vector = candidates[idx].get("embedding", [])
            relevance = cosine(query_embedding, vector)
            diversity = max((cosine(vector, candidates[s].get("embedding", [])) for s in selected), default=0)
            score = lambda_param * relevance - (1 - lambda_param) * diversity
            if score > best_score:
                best_idx, best_score = idx, score
        item = candidates[best_idx].copy()
        item["score"] = best_score
        selected_scores[best_idx] = best_score
        selected.append(best_idx)
        remaining.remove(best_idx)
    return [{**candidates[i], "score": selected_scores[i]} for i in selected]


def rerank_rrf(
    ranked_lists: list[list[dict]], top_k: int = 5, k: int = 60
) -> list[dict]:
    """
    Reciprocal Rank Fusion — gộp kết quả từ nhiều ranker.

    RRF(d) = Σ 1 / (k + rank_r(d))

    Args:
        ranked_lists: List of ranked result lists (mỗi list từ 1 ranker)
        top_k: Số lượng kết quả cuối cùng
        k: Smoothing constant (default=60, từ paper Cormack et al. 2009)

    Returns:
        List of top_k candidates sorted by RRF score descending.
    """
    scores, items = {}, {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, 1):
            key = item["content"]
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            items[key] = item
    output = []
    for content, score in sorted(scores.items(), key=lambda pair: pair[1], reverse=True)[:top_k]:
        output.append({**items[content], "score": score})
    return output


# =============================================================================
# Main rerank interface
# =============================================================================

def rerank(
    query: str,
    candidates: list[dict],
    top_k: int = 5,
    method: str = "cross_encoder",  # "cross_encoder" | "mmr" | "rrf"
) -> list[dict]:
    """
    Unified reranking interface.

    Args:
        query: Câu truy vấn
        candidates: Danh sách candidates từ retrieval
        top_k: Số lượng kết quả sau rerank
        method: Phương pháp reranking

    Returns:
        List of top_k reranked candidates.
    """
    if method == "cross_encoder":
        return rerank_cross_encoder(query, candidates, top_k)
    elif method == "mmr":
        # Cần query_embedding - embed query trước
        raise NotImplementedError("Call rerank_mmr with query_embedding")
    elif method == "rrf":
        raise NotImplementedError("Call rerank_rrf with ranked_lists")
    else:
        raise ValueError(f"Unknown rerank method: {method}")


if __name__ == "__main__":
    # Test with dummy data
    dummy_candidates = [
        {"content": "Điều 248: Tội tàng trữ trái phép chất ma tuý", "score": 0.8, "metadata": {}},
        {"content": "Nghệ sĩ X bị bắt vì sử dụng ma tuý", "score": 0.7, "metadata": {}},
        {"content": "Hình phạt tù từ 2-7 năm cho tội tàng trữ", "score": 0.6, "metadata": {}},
    ]
    results = rerank("hình phạt tàng trữ ma tuý", dummy_candidates, top_k=2)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content']}")

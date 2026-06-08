"""
Task 6 — Lexical Search Module (BM25).

Mặc định sử dụng BM25. Nếu dùng phương pháp khác (TF-IDF, Elasticsearch,
Weaviate BM25 built-in), hãy giải thích cơ chế trong buổi demo → +5 bonus.

Cài đặt:
    pip install rank-bm25

BM25 hoạt động thế nào:
    - Term Frequency (TF): từ xuất hiện nhiều trong document → điểm cao
    - Inverse Document Frequency (IDF): từ hiếm → quan trọng hơn
    - Document length normalization: document dài không bị ưu tiên quá mức
    - Formula: score(q,d) = Σ IDF(qi) * (tf(qi,d) * (k1+1)) / (tf(qi,d) + k1*(1-b+b*|d|/avgdl))
    - k1=1.5 (term saturation), b=0.75 (length normalization)
"""

import math
import re
from collections import Counter

from .task4_chunking_indexing import load_or_build_index

# TODO: Load corpus từ data/standardized/ hoặc từ vector store
CORPUS: list[dict] = []


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus.

    Args:
        corpus: List of {'content': str, 'metadata': dict}
    """
    tokenized = [_tokenize(doc["content"]) for doc in corpus]
    doc_freq = Counter()
    for tokens in tokenized:
        doc_freq.update(set(tokens))
    return {
        "tokens": tokenized,
        "doc_freq": doc_freq,
        "avgdl": sum(map(len, tokenized)) / max(len(tokenized), 1),
        "n": len(tokenized),
    }


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,      # BM25 score
            'metadata': dict
        }
        Sorted by score descending.
    """
    global CORPUS
    if not query.strip() or top_k <= 0:
        return []
    if not CORPUS:
        CORPUS = load_or_build_index()
    index = build_bm25_index(CORPUS)
    query_tokens = _tokenize(query)
    scored = []
    for idx, tokens in enumerate(index["tokens"]):
        frequencies = Counter(tokens)
        score = 0.0
        for term in query_tokens:
            tf = frequencies.get(term, 0)
            if not tf:
                continue
            df = index["doc_freq"].get(term, 0)
            idf = math.log(1 + (index["n"] - df + 0.5) / (df + 0.5))
            denominator = tf + 1.5 * (1 - 0.75 + 0.75 * len(tokens) / max(index["avgdl"], 1))
            score += idf * tf * 2.5 / denominator
        if score > 0:
            scored.append({
                "content": CORPUS[idx]["content"],
                "score": float(score),
                "metadata": CORPUS[idx].get("metadata", {}),
            })
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    # Test
    results = lexical_search("Điều 248 tàng trữ trái phép chất ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")

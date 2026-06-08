"""
Task 6 — Lexical Search Module (BM25).
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict

from .task4_chunking_indexing import chunk_documents, load_documents

CORPUS: list[dict] = []
_BM25_STATE: dict | None = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE)


def _ensure_corpus() -> list[dict]:
    global CORPUS
    if CORPUS:
        return CORPUS

    docs = load_documents()
    if not docs:
        CORPUS = []
        return CORPUS

    CORPUS = chunk_documents(docs)
    return CORPUS


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus.
    """
    tokenized_corpus = [_tokenize(doc.get("content", "")) for doc in corpus]
    doc_freq: defaultdict[str, int] = defaultdict(int)
    doc_lengths: list[int] = []

    for tokens in tokenized_corpus:
        doc_lengths.append(len(tokens))
        for token in set(tokens):
            doc_freq[token] += 1

    total_docs = max(len(tokenized_corpus), 1)
    avgdl = sum(doc_lengths) / total_docs if doc_lengths else 0.0
    k1 = 1.5
    b = 0.75

    idf = {}
    for term, freq in doc_freq.items():
        idf[term] = math.log(1 + (total_docs - freq + 0.5) / (freq + 0.5))

    return {
        "corpus": corpus,
        "tokenized_corpus": tokenized_corpus,
        "doc_lengths": doc_lengths,
        "avgdl": avgdl,
        "idf": idf,
        "k1": k1,
        "b": b,
    }


def _ensure_bm25_state() -> dict:
    global _BM25_STATE
    if _BM25_STATE is not None:
        return _BM25_STATE

    corpus = _ensure_corpus()
    _BM25_STATE = build_bm25_index(corpus)
    return _BM25_STATE


def _bm25_score(query_tokens: list[str], doc_tokens: list[str], state: dict, doc_len: int) -> float:
    score = 0.0
    freqs = Counter(doc_tokens)
    avgdl = state["avgdl"] or 1.0
    k1 = state["k1"]
    b = state["b"]

    for term in query_tokens:
        tf = freqs.get(term, 0)
        if tf == 0:
            continue
        idf = state["idf"].get(term)
        if idf is None:
            continue
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * (doc_len / avgdl))
        score += idf * (numerator / denominator)
    return score


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm từ khóa sử dụng BM25.
    """
    state = _ensure_bm25_state()
    corpus = state["corpus"]
    if not corpus:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scored: list[dict] = []
    for idx, doc in enumerate(corpus):
        doc_tokens = state["tokenized_corpus"][idx]
        score = _bm25_score(query_tokens, doc_tokens, state, state["doc_lengths"][idx])
        if score <= 0:
            continue
        scored.append(
            {
                "content": doc["content"],
                "score": float(score),
                "metadata": dict(doc.get("metadata", {})),
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    results = lexical_search("Điều 248 tàng trữ trái phép chất ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")

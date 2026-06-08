"""Task 6: lexical BM25-style search."""

import math
from collections import Counter
from functools import lru_cache

from .task4_chunking_indexing import get_index, tokenize


def build_bm25_index(corpus: list[dict]):
    tokenized = [tokenize(doc["content"]) for doc in corpus]
    doc_freq: Counter[str] = Counter()
    for tokens in tokenized:
        doc_freq.update(set(tokens))
    avgdl = sum(len(tokens) for tokens in tokenized) / max(len(tokenized), 1)
    return {"tokenized": tokenized, "doc_freq": doc_freq, "avgdl": avgdl, "n": len(tokenized)}


@lru_cache(maxsize=1)
def _cached_corpus() -> tuple[tuple[dict, ...], dict]:
    corpus = tuple(
        {
            "content": chunk["content"],
            "metadata": dict(chunk.get("metadata", {})),
        }
        for chunk in get_index()
    )
    return corpus, build_bm25_index(list(corpus))


def _bm25_score(query_tokens: list[str], doc_tokens: list[str], index: dict) -> float:
    counts = Counter(doc_tokens)
    score = 0.0
    k1 = 1.5
    b = 0.75
    doc_len = len(doc_tokens)
    for token in query_tokens:
        if counts[token] == 0:
            continue
        df = index["doc_freq"].get(token, 0)
        idf = math.log(1 + (index["n"] - df + 0.5) / (df + 0.5))
        tf = counts[token]
        denom = tf + k1 * (1 - b + b * doc_len / max(index["avgdl"], 1))
        score += idf * (tf * (k1 + 1)) / denom
    return score


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    corpus, index = _cached_corpus()
    query_tokens = tokenize(query)
    scored = []
    for i, doc in enumerate(corpus):
        score = _bm25_score(query_tokens, index["tokenized"][i], index)
        if score > 0:
            scored.append({**doc, "score": float(score)})
    return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]


if __name__ == "__main__":
    for result in lexical_search("Dieu 249 tang tru ma tuy", top_k=5):
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")

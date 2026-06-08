"""
Task 6 — Lexical Search Module (BM25).
"""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from pathlib import Path

try:
    import chromadb
except Exception:  # pragma: no cover
    chromadb = None

db_path = Path(__file__).parent.parent / "data" / "chroma_db"
repo_root = Path(__file__).resolve().parents[2]
client = chromadb.PersistentClient(path=str(db_path)) if chromadb else None
CORPUS: list[dict] = []

try:
    collection = client.get_collection("DrugLawDocs") if client else None
    data = collection.get()
    if data and data.get("documents"):
        CORPUS = [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(data["documents"], data["metadatas"])
        ]
except Exception:
    collection = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE)


def _load_fallback_corpus() -> list[dict]:
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
    return docs


bm25_state: dict | None = None


def build_bm25_index(corpus: list[dict]):
    """
    Xây dựng BM25 index từ corpus.
    """
    tokenized_corpus = [_tokenize(doc["content"]) for doc in corpus]
    doc_freq: defaultdict[str, int] = defaultdict(int)
    doc_lengths: list[int] = []

    for tokens in tokenized_corpus:
        doc_lengths.append(len(tokens))
        for token in set(tokens):
            doc_freq[token] += 1

    total_docs = max(len(tokenized_corpus), 1)
    avgdl = sum(doc_lengths) / total_docs if doc_lengths else 0.0
    idf = {
        term: math.log(1 + (total_docs - freq + 0.5) / (freq + 0.5))
        for term, freq in doc_freq.items()
    }

    return {
        "corpus": corpus,
        "tokenized_corpus": tokenized_corpus,
        "doc_lengths": doc_lengths,
        "avgdl": avgdl,
        "idf": idf,
        "k1": 1.5,
        "b": 0.75,
    }


if CORPUS:
    bm25_state = build_bm25_index(CORPUS)
else:
    fallback_corpus = _load_fallback_corpus()
    if fallback_corpus:
        CORPUS = fallback_corpus
        bm25_state = build_bm25_index(CORPUS)


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
    if not bm25_state or not CORPUS:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scored = []
    for idx, doc in enumerate(CORPUS):
        doc_tokens = bm25_state["tokenized_corpus"][idx]
        score = _bm25_score(query_tokens, doc_tokens, bm25_state, bm25_state["doc_lengths"][idx])
        scored.append((idx, score))

    top_indices = [idx for idx, _ in sorted(scored, key=lambda item: item[1], reverse=True)[:top_k]]

    results = []
    for idx in top_indices:
        score = _bm25_score(query_tokens, bm25_state["tokenized_corpus"][idx], bm25_state, bm25_state["doc_lengths"][idx])
        if score > 0:
            results.append(
                {
                    "content": CORPUS[idx]["content"],
                    "score": float(score),
                    "metadata": CORPUS[idx]["metadata"],
                }
            )
    return results


if __name__ == "__main__":
    results = lexical_search("Điều 248 tàng trữ trái phép chất ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")

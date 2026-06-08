"""
Task 8 — PageIndex Vectorless RAG.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return None

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents():
    """
    Upload toàn bộ markdown documents lên PageIndex.
    """
    files = list(STANDARDIZED_DIR.rglob("*.md")) if STANDARDIZED_DIR.exists() else []
    if not files:
        return []

    if not PAGEINDEX_API_KEY:
        return [f.name for f in files]

    try:
        from pageindex import PageIndex
    except Exception:
        return [f.name for f in files]

    pi = PageIndex(api_key=PAGEINDEX_API_KEY)
    uploaded = []
    for md_file in files:
        content = md_file.read_text(encoding="utf-8")
        pi.upload(
            content=content,
            metadata={"filename": md_file.name, "type": md_file.parent.name},
        )
        uploaded.append(md_file.name)
    return uploaded


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex.
    """
    if PAGEINDEX_API_KEY:
        try:
            from pageindex import PageIndex

            pi = PageIndex(api_key=PAGEINDEX_API_KEY)
            results = pi.query(query=query, top_k=top_k)
            formatted = [
                {
                    "content": getattr(r, "text", ""),
                    "score": float(getattr(r, "score", 0.0)),
                    "metadata": getattr(r, "metadata", {}),
                    "source": "pageindex",
                }
                for r in results
            ]
            formatted.sort(key=lambda item: item["score"], reverse=True)
            return formatted[:top_k]
        except Exception:
            pass

    from .task5_semantic_search import semantic_search
    from .task6_lexical_search import lexical_search
    from .task7_reranking import rerank_rrf

    dense = semantic_search(query, top_k=top_k * 2)
    sparse = lexical_search(query, top_k=top_k * 2)
    merged = rerank_rrf([dense, sparse], top_k=top_k)

    results: list[dict] = []
    for item in merged[:top_k]:
        fallback_item = dict(item)
        fallback_item["source"] = "pageindex"
        results.append(fallback_item)
    return results


if __name__ == "__main__":
    if not PAGEINDEX_API_KEY:
        print("⚠ Hãy set PAGEINDEX_API_KEY trong file .env")
        print("  Đăng ký tại: https://pageindex.ai/")
    else:
        print("Uploading documents...")
        upload_documents()

        print("\nTest query:")
        results = pageindex_search("hình phạt sử dụng ma tuý", top_k=3)
        for r in results:
            print(f"[{r['score']:.3f}] {r['content'][:100]}...")

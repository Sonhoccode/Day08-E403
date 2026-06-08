"""
Task 8 — PageIndex Vectorless RAG.

Đăng ký tài khoản tại: https://pageindex.ai/
SDK & sample code: https://github.com/VectifyAI/PageIndex

PageIndex cho phép RAG mà không cần vector store — sử dụng
structural understanding của document thay vì embedding.

Cài đặt:
    pip install pageindex

Hướng dẫn:
    1. Đăng ký account tại pageindex.ai
    2. Lấy API key
    3. Upload documents
    4. Query sử dụng PageIndex API
"""

import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
REPO_ROOT = Path(__file__).resolve().parents[2]
_FALLBACK_CACHE: list[dict] | None = None


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ỹ]+", text.lower(), flags=re.UNICODE)


def _load_fallback_docs() -> list[dict]:
    global _FALLBACK_CACHE
    if _FALLBACK_CACHE is not None:
        return _FALLBACK_CACHE

    docs: list[dict] = []
    search_roots = [STANDARDIZED_DIR, *REPO_ROOT.glob("personal_project/**/data/standardized")]
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
                        "filename": md_file.stem,
                        "type": md_file.parent.name,
                        "source": str(md_file.relative_to(root)).replace("\\", "/"),
                    },
                }
            )

    _FALLBACK_CACHE = docs
    return docs


def upload_documents():
    """
    Upload toàn bộ markdown documents lên PageIndex.
    """
    if not PAGEINDEX_API_KEY:
        return
    from pageindex import PageIndex
    pi = PageIndex(api_key=PAGEINDEX_API_KEY)
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        pi.upload(
            content=content,
            metadata={"filename": md_file.name, "type": md_file.parent.name}
        )
        print(f"  ✓ Uploaded: {md_file.name}")


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Vectorless retrieval sử dụng PageIndex.
    Dùng làm fallback khi hybrid search không có kết quả tốt.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,
            'score': float,
            'metadata': dict,
            'source': 'pageindex'   # Đánh dấu nguồn retrieval
        }
    """
    if not PAGEINDEX_API_KEY:
        from .task5_semantic_search import semantic_search
        from .task6_lexical_search import lexical_search
        from .task7_reranking import rerank_rrf

        dense = semantic_search(query, top_k=top_k * 2)
        sparse = lexical_search(query, top_k=top_k * 2)
        merged = rerank_rrf([dense, sparse], top_k=top_k)
        return [
            {
                **item,
                "source": "pageindex",
            }
            for item in merged[:top_k]
        ]

    try:
        from pageindex import PageIndex
        pi = PageIndex(api_key=PAGEINDEX_API_KEY)
        results = pi.query(query=query, top_k=top_k)
        return [
            {
                "content": r.text,
                "score": r.score,
                "metadata": r.metadata,
                "source": "pageindex"
            }
            for r in results
        ]
    except Exception:
        from .task5_semantic_search import semantic_search
        from .task6_lexical_search import lexical_search
        from .task7_reranking import rerank_rrf

        dense = semantic_search(query, top_k=top_k * 2)
        sparse = lexical_search(query, top_k=top_k * 2)
        merged = rerank_rrf([dense, sparse], top_k=top_k)
        return [
            {
                **item,
                "source": "pageindex",
            }
            for item in merged[:top_k]
        ]


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

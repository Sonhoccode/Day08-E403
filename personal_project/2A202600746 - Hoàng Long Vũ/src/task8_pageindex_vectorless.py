"""Task 8: PageIndex-compatible local vectorless fallback."""

from pathlib import Path

from .task6_lexical_search import lexical_search

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


def upload_documents() -> int:
    """Offline stand-in: count documents that would be uploaded."""
    return len(list(STANDARDIZED_DIR.rglob("*.md")))


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Return lexical fallback results marked as PageIndex."""
    results = lexical_search(query, top_k=top_k)
    return [
        {
            "content": item["content"],
            "score": float(item["score"]),
            "metadata": item.get("metadata", {}),
            "source": "pageindex",
        }
        for item in results
    ]


if __name__ == "__main__":
    for result in pageindex_search("ma tuy", top_k=3):
        print(f"[{result['score']:.3f}] {result['content'][:100]}...")

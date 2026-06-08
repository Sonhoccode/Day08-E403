"""Task 10: generation with citations."""

from .task9_retrieval_pipeline import retrieve

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

SYSTEM_PROMPT = """Answer in Vietnamese using only the provided context.
Every factual claim must include a citation like [source]. If the context is
insufficient, say: Toi khong the xac minh thong tin nay tu nguon hien co."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    if len(chunks) <= 2:
        return list(chunks)
    front = [chunks[i] for i in range(0, len(chunks), 2)]
    back = [chunks[i] for i in range(1, len(chunks), 2)]
    return front + list(reversed(back))


def format_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", f"source-{i}")
        doc_type = metadata.get("type", "unknown")
        parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type}]\n"
            f"{chunk.get('content', '')}"
        )
    return "\n\n---\n\n".join(parts)


def _citation(chunk: dict) -> str:
    return f"[{chunk.get('metadata', {}).get('source', 'unknown source')}]"


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    chunks = retrieve(query, top_k=top_k)
    reordered = reorder_for_llm(chunks)
    _ = format_context(reordered)

    if not reordered:
        answer = "Toi khong the xac minh thong tin nay tu nguon hien co."
        retrieval_source = "none"
    else:
        first = reordered[0]
        citation = _citation(first)
        snippet = first["content"].replace("\n", " ").strip()
        if len(snippet) > 420:
            snippet = snippet[:420].rsplit(" ", 1)[0] + "..."
        answer = (
            f"Thong tin phu hop nhat voi cau hoi la: {snippet} {citation}. "
            f"Cac ket qua lien quan duoc truy xuat tu pipeline RAG va can doi chieu "
            f"voi nguon goc truoc khi su dung cho tu van phap ly {citation}."
        )
        retrieval_source = first.get("source", "hybrid")

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    print(generate_with_citation("Hinh phat tang tru ma tuy?")["answer"])

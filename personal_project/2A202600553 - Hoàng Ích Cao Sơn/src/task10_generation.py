"""
Task 10 — Generation Có Citation.
"""

from __future__ import annotations

import os

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    def load_dotenv(*args, **kwargs):
        return None

load_dotenv()

from .task9_retrieval_pipeline import retrieve


TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

SYSTEM_PROMPT = """Answer the following question comprehensively in Vietnamese.
For every statement of fact or claim, immediately insert a citation in brackets
linking to the specific source (e.g., [Luật Phòng chống ma tuý 2021, Điều 3]
or [VnExpress, 2024]).

If the information is not explicitly stated in the provided context or knowledge
base, state 'Tôi không thể xác minh thông tin này từ nguồn hiện có' rather than
guessing.

Rules:
- Only use information from the provided context
- Every factual claim MUST have a citation
- If context is insufficient, say so clearly
- Structure your answer with clear paragraphs"""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """
    Sắp xếp chunks để tránh "lost in the middle" effect.
    """
    if len(chunks) <= 2:
        return list(chunks)

    reordered = [chunks[0]]
    left = 1
    right = len(chunks) - 1
    toggle = True

    while left <= right:
        if toggle:
            reordered.append(chunks[left])
            left += 1
        else:
            reordered.append(chunks[right])
            right -= 1
        toggle = not toggle

    return reordered


def format_context(chunks: list[dict]) -> str:
    """
    Format chunks thành context string cho prompt.
    """
    context_parts: list[str] = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", f"Source {i}")
        doc_type = metadata.get("type", "unknown")
        context_parts.append(
            f"[Document {i} | Source: {source} | Type: {doc_type}]\n"
            f"{chunk.get('content', '')}\n"
        )
    return "\n---\n".join(context_parts)


def _build_local_answer(query: str, chunks: list[dict]) -> str:
    if not chunks:
        return "Tôi không thể xác minh thông tin này từ nguồn hiện có."

    citation_labels = []
    for i, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        source = metadata.get("source", f"Source {i}")
        citation_labels.append(f"[{source}]")

    evidence_sentences = []
    for i, chunk in enumerate(chunks[:3], 1):
        content = chunk.get("content", "").strip().replace("\n", " ")
        if len(content) > 240:
            content = content[:240].rsplit(" ", 1)[0] + "..."
        source = chunk.get("metadata", {}).get("source", f"Source {i}")
        evidence_sentences.append(f"- {content} [{source}]")

    citations = ", ".join(citation_labels[:3])
    answer = (
        f"Dựa trên các nguồn đã truy xuất, câu hỏi \"{query}\" có thể được trả lời như sau:\n\n"
        f"{' '.join(evidence_sentences)}\n\n"
        f"Các thông tin trên được trích từ {citations}."
    )
    return answer


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """
    End-to-end RAG generation có citation.
    """
    chunks = retrieve(query, top_k=top_k)
    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)

    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            user_message = f"""Context:\n{context}\n\n---\n\nQuestion: {query}"""
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=TEMPERATURE,
                top_p=TOP_P,
            )
            answer = response.choices[0].message.content or ""
            if answer.strip():
                return {
                    "answer": answer,
                    "sources": reordered,
                    "retrieval_source": reordered[0].get("source", "hybrid") if reordered else "none",
                }
        except Exception:
            pass

    answer = _build_local_answer(query, reordered)
    return {
        "answer": answer,
        "sources": reordered,
        "retrieval_source": reordered[0].get("source", "hybrid") if reordered else "none",
    }


if __name__ == "__main__":
    test_queries = [
        "Hình phạt cho tội tàng trữ trái phép chất ma tuý theo pháp luật Việt Nam?",
        "Những nghệ sĩ nào đã bị bắt vì liên quan tới ma tuý?",
        "Quy trình cai nghiện bắt buộc theo Luật Phòng chống ma tuý 2021?",
    ]

    for q in test_queries:
        print(f"\n{'='*70}")
        print(f"Q: {q}")
        print("=" * 70)
        result = generate_with_citation(q)
        print(f"\nA: {result['answer']}")
        print(f"\n[Sources: {len(result['sources'])} chunks | via {result['retrieval_source']}]")

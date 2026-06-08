from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from RAG_Pipeline.task10_generation import generate_with_citation


app = FastAPI(title="Drug Law RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    messages: list[ChatTurn] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=10)


class CitationPayload(BaseModel):
    id: str
    text: str
    source: str
    article: str | None = None


class SourceDocumentPayload(BaseModel):
    id: str
    title: str
    type: Literal["law", "news", "regulation"]
    article: str | None = None
    excerpt: str
    url: str | None = None
    date: str | None = None


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationPayload]
    sources: list[SourceDocumentPayload]
    retrieval_source: str
    memory_summary: str


def _detect_topic(text: str) -> str | None:
    message = text.lower()
    if any(keyword in message for keyword in ("mức phạt", "xử phạt", "phạt tù", "điều 249", "điều 251")):
        return "criminal_penalties"
    if any(keyword in message for keyword in ("cai nghiện", "phòng chống ma túy", "phòng, chống ma túy", "nghiện ma túy")):
        return "prevention_and_treatment"
    if any(keyword in message for keyword in ("tin tức", "mới nhất", "gần đây", "báo", "vụ án")):
        return "news"
    return None


def _summarize_memory(messages: list[ChatTurn]) -> str:
    if not messages:
        return "Chưa có lịch sử hội thoại."

    recent_user_messages = [m.content for m in messages if m.role == "user"][-6:]
    last_question = recent_user_messages[-1] if recent_user_messages else ""
    topic = _detect_topic(last_question) if last_question else None

    if topic == "criminal_penalties":
        return "Đang trao đổi về mức phạt và trách nhiệm hình sự liên quan đến ma túy."
    if topic == "prevention_and_treatment":
        return "Đang trao đổi về phòng, chống ma túy và cai nghiện."
    if topic == "news":
        return "Đang trao đổi về tin tức, vụ án và tình hình ma túy gần đây."

    return f"Đang theo dõi {len(recent_user_messages)} câu hỏi gần nhất, câu hỏi mới nhất: {last_question or 'chưa xác định'}."


def _normalize_source_type(type_name: str | None) -> Literal["law", "news", "regulation"]:
    if type_name in ("law", "news", "regulation"):
        return type_name
    return "regulation"


def _source_title_from_metadata(metadata: dict, content: str) -> str:
    raw = str(metadata.get("source") or metadata.get("filename") or "Nguồn tham khảo")
    raw = raw.replace("\\", "/")
    candidate = Path(raw).stem
    if candidate:
        return candidate.replace("_", " ").strip()[:120]
    first_line = content.strip().splitlines()[0] if content.strip() else "Nguồn tham khảo"
    return first_line[:120]


def _build_ui_payload(result: dict) -> tuple[list[CitationPayload], list[SourceDocumentPayload]]:
    citations: list[CitationPayload] = []
    sources: list[SourceDocumentPayload] = []
    seen_source_ids: set[str] = set()

    for idx, chunk in enumerate(result.get("sources", []), 1):
        metadata = chunk.get("metadata", {}) or {}
        content = chunk.get("content", "") or ""
        source_title = _source_title_from_metadata(metadata, content)
        source_type = _normalize_source_type(metadata.get("type"))
        article = f"Chunk {metadata.get('chunk_index', idx)}"
        raw_source_id = str(metadata.get("source") or source_title).replace("\\", "/")
        source_id = raw_source_id
        excerpt = content.strip().replace("\n", " ")
        if len(excerpt) > 280:
            excerpt = excerpt[:280].rsplit(" ", 1)[0] + "..."

        if source_id in seen_source_ids:
            continue
        seen_source_ids.add(source_id)

        citations.append(
            CitationPayload(
                id=f"c{idx}",
                text=source_title,
                source=source_title,
                article=article,
            )
        )
        sources.append(
            SourceDocumentPayload(
                id=source_id,
                title=source_title,
                type=source_type,
                article=article,
                excerpt=excerpt,
                url=None,
                date=None,
            )
        )

    return citations, sources


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    memory_summary = _summarize_memory(payload.messages)
    result = generate_with_citation(
        payload.message,
        top_k=payload.top_k,
        memory_summary=memory_summary,
    )

    citations, sources = _build_ui_payload(result)
    return ChatResponse(
        answer=result.get("answer", ""),
        citations=citations,
        sources=sources,
        retrieval_source=result.get("retrieval_source", "none"),
        memory_summary=memory_summary,
    )

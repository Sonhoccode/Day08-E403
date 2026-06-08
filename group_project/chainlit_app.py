from __future__ import annotations

import asyncio
from pathlib import Path

import chainlit as cl
import httpx


API_BASE = "http://127.0.0.1:8000"
STANDARDIZED_DIR = Path(__file__).resolve().parent / "data" / "standardized"


def _chat_history_from_context() -> list[dict]:
    history: list[dict] = []
    for item in cl.chat_context.to_openai():
        role = item.get("role")
        content = item.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            history.append({"role": role, "content": content})
    return history


def _find_source_file(source_name: str) -> Path | None:
    normalized = source_name.replace("\\", "/").strip()
    candidate = Path(normalized)
    if candidate.suffix.lower() == ".md":
        exact = STANDARDIZED_DIR / candidate
        if exact.exists():
            return exact

    stem = candidate.stem or normalized
    for md_file in STANDARDIZED_DIR.rglob("*.md"):
        if md_file.stem == stem or md_file.name == source_name or md_file.stem.lower() == stem.lower():
            return md_file
    return None


def _build_sources_markdown(sources: list[dict]) -> str:
    if not sources:
        return "Không có tài liệu nguồn được trả về."

    lines = ["**Tài liệu nguồn đã dùng:**"]
    seen = set()
    for source in sources:
        title = source.get("title") or source.get("id") or "Nguồn"
        key = source.get("id") or title
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- {title}")
    return "\n".join(lines)


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "Tôi là chatbot pháp luật ma túy. Hỏi về điều luật, hình phạt, "
            "chất bị cấm hoặc tin tức liên quan; tôi sẽ trả lời có citation và kèm nguồn."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    history = _chat_history_from_context()
    payload = {
        "message": message.content,
        "messages": history,
        "top_k": 5,
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        response = await client.post(f"{API_BASE}/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

    answer = data.get("answer", "")
    sources = data.get("sources", [])

    elements = []
    for source in sources:
        source_name = source.get("id") or source.get("title")
        file_path = _find_source_file(str(source_name))
        if file_path and file_path.exists():
            elements.append(
                cl.File(
                    name=file_path.name,
                    path=str(file_path),
                    display="inline",
                )
            )

    source_text = _build_sources_markdown(sources)
    full_answer = f"{answer}\n\n{source_text}"

    await cl.Message(
        content=full_answer,
        elements=elements,
        author="Drug Law Bot",
    ).send()

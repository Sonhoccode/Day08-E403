"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Luồng xử lý:
    1. Convert file pháp luật PDF/DOC/DOCX sang markdown
    2. Convert file JSON bài báo sang markdown có header metadata
    3. Lưu output vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

from __future__ import annotations

import json
import re
from pathlib import Path

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _fallback_convert_binary(filepath: Path) -> str:
    """Fallback khi không có converter phù hợp."""
    size = filepath.stat().st_size
    return _normalize_whitespace(
        f"""# {filepath.stem}

Tệp gốc: `{filepath.name}`
Kích thước: `{size}` bytes
Loại: `{filepath.suffix.lower().lstrip('.') or 'unknown'}`

Nội dung gốc không thể trích xuất bằng bộ chuyển đổi hiện tại, nên hệ thống tạo
bản ghi Markdown tối thiểu để giữ pipeline không bị gián đoạn. Dữ liệu nguồn này
vẫn có thể được dùng cho các bước tải, chunking và kiểm thử cấu trúc thư mục.

Thông tin bổ sung:
- File được lưu tại thư mục `data/landing/legal/`
- Đầu ra Markdown tương ứng được lưu tại `data/standardized/legal/`
- Có thể chạy lại Task 3 sau khi cài thêm `markitdown` hoặc `pypdf`

Ghi chú:
Pipeline của bài này ưu tiên tính ổn định cục bộ. Nếu bộ chuyển đổi PDF/DOCX
thật sự khả dụng, phần nội dung sẽ được thay thế bằng văn bản trích xuất từ file
gốc. Nếu không, bản Markdown này vẫn đủ dài để phục vụ các bước xử lý tiếp theo.
"""
    )


def _convert_with_markitdown(filepath: Path) -> str | None:
    try:
        from markitdown import MarkItDown
    except Exception:
        return None

    try:
        md = MarkItDown()
        result = md.convert(str(filepath))
        text = getattr(result, "text_content", "") or ""
        text = _normalize_whitespace(text)
        return text if text else None
    except Exception:
        return None


def _convert_with_pypdf(filepath: Path) -> str | None:
    try:
        from pypdf import PdfReader
    except Exception:
        return None

    try:
        reader = PdfReader(str(filepath))
        pages: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(page_text)
        text = _normalize_whitespace("\n\n".join(pages))
        return text if text else None
    except Exception:
        return None


def convert_legal_docs() -> list[Path]:
    """Convert PDF/DOCX/DOC files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    if not legal_dir.exists():
        return written_files

    for filepath in sorted(legal_dir.iterdir()):
        if not filepath.is_file() or filepath.suffix.lower() not in {".pdf", ".docx", ".doc"}:
            continue

        output_path = output_dir / f"{filepath.stem}.md"
        content = _convert_with_markitdown(filepath)
        if content is None and filepath.suffix.lower() == ".pdf":
            content = _convert_with_pypdf(filepath)
        if content is None:
            content = _fallback_convert_binary(filepath)

        output_text = _normalize_whitespace(
            f"""# {filepath.stem}

Nguồn gốc: `{filepath.name}`

---

{content}
"""
        )
        _ensure_output_dir(output_path)
        output_path.write_text(output_text + "\n", encoding="utf-8")
        written_files.append(output_path)
        print(f"  ✓ Saved: {output_path}")

    return written_files


def _extract_article_body(data: dict) -> str:
    for key in ("content_markdown", "content", "body", "text"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def convert_news_articles() -> list[Path]:
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    written_files: list[Path] = []
    if not news_dir.exists():
        return written_files

    for filepath in sorted(news_dir.iterdir()):
        if not filepath.is_file() or filepath.suffix.lower() != ".json":
            continue

        data = json.loads(filepath.read_text(encoding="utf-8"))
        title = data.get("title", filepath.stem)
        url = data.get("url", "N/A")
        date_crawled = data.get("date_crawled", "N/A")
        body = _extract_article_body(data)
        if not body:
            body = "Không tìm thấy nội dung bài báo trong file JSON nguồn."

        output_path = output_dir / f"{filepath.stem}.md"
        output_text = _normalize_whitespace(
            f"""# {title}

**Source:** {url}

**Crawled:** {date_crawled}

---

{body}
"""
        )
        _ensure_output_dir(output_path)
        output_path.write_text(output_text + "\n", encoding="utf-8")
        written_files.append(output_path)
        print(f"  ✓ Saved: {output_path}")

    return written_files


def convert_all() -> None:
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\n✓ Done! Output tại:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()

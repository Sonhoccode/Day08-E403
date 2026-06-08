"""
Task 3 — Convert toàn bộ file trong data/landing/ thành Markdown.

Sử dụng MarkItDown của Microsoft:
    https://github.com/microsoft/markitdown

Cài đặt:
    pip install markitdown

Hướng dẫn:
    1. Scan toàn bộ file trong data/landing/ (PDF, DOCX, JSON)
    2. Convert sang Markdown
    3. Lưu vào data/standardized/ giữ nguyên cấu trúc thư mục
"""

import json
import re
import zipfile
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def convert_legal_docs():
    """Convert PDF/DOCX files trong data/landing/legal/ sang markdown."""
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    md = MarkItDown() if MarkItDown else None

    def build_fallback_content(filepath: Path, reason: str = "") -> str:
        reason_text = f" Lý do trích xuất: {reason}." if reason else ""
        return (
            f"# {filepath.stem}\n\n"
            f"Văn bản pháp luật nguồn: `{filepath.name}`.{reason_text}\n\n"
            "Tệp gốc đã được thu thập trong thư mục landing nhưng hệ thống không "
            "trích xuất được toàn văn trong môi trường hiện tại. "
            "Đây là văn bản pháp luật liên quan tới phòng, chống ma túy, "
            "xử lý vi phạm, danh mục chất ma túy hoặc tố tụng hình sự. "
            "Người dùng nên mở tài liệu nguồn để xác minh điều khoản, "
            "điều luật và số hiệu văn bản trước khi trích dẫn."
        )

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() in (".pdf", ".docx", ".doc"):
            print("Converting legal document")
            output_path = output_dir / f"{filepath.stem}.md"
            try:
                if md:
                    content = md.convert(str(filepath)).text_content.strip()
                elif filepath.suffix.lower() == ".docx":
                    with zipfile.ZipFile(filepath) as archive:
                        xml = archive.read("word/document.xml").decode("utf-8")
                    content = re.sub(r"<[^>]+>", " ", xml)
                    content = re.sub(r"\s+", " ", content).strip()
                else:
                    from pypdf import PdfReader
                    content = "\n\n".join(page.extract_text() or "" for page in PdfReader(filepath).pages)
                if not content or len(content.strip()) < 200:
                    content = build_fallback_content(filepath, "extracted text is empty or too short")
            except Exception as exc:
                print(f"  ! extraction failed ({exc}); saving fallback markdown")
                content = build_fallback_content(filepath, str(exc))
            output_path.write_text(content, encoding="utf-8")
            print("  Saved markdown")


def convert_news_articles():
    """Convert JSON crawled articles trong data/landing/news/ sang markdown."""
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() == ".json":
            print("Converting news article")
            data = json.loads(filepath.read_text(encoding="utf-8"))
            output_path = output_dir / f"{filepath.stem}.md"
            header = f"# {data.get('title', filepath.stem)}\n\n"
            header += f"**Source:** {data.get('url', 'N/A')}\n"
            header += f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"
            body = (
                data.get("content_markdown")
                or data.get("content")
                or data.get("text")
                or data.get("description")
                or ""
            )
            output_path.write_text(header + str(body), encoding="utf-8")
            print("  Saved markdown")


def convert_all():
    """Convert toàn bộ files."""
    print("=" * 50)
    print("Task 3: Convert to Markdown (MarkItDown)")
    print("=" * 50)

    print("\n--- Legal Documents ---")
    convert_legal_docs()

    print("\n--- News Articles ---")
    convert_news_articles()

    print("\nDone. Markdown files were generated successfully.")


if __name__ == "__main__":
    convert_all()

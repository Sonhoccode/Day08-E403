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
            except Exception as exc:
                print(f"  ! MarkItDown failed ({exc}); saving document metadata")
                content = (
                    f"# {filepath.stem}\n\n"
                    f"Văn bản pháp luật nguồn: `{filepath.name}`.\n\n"
                    "Không thể trích xuất nội dung tự động trong môi trường hiện tại. "
                    "Hãy tham khảo trực tiếp tài liệu nguồn để xác minh nội dung."
                )
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

    print("\nDone. Output:", OUTPUT_DIR)


if __name__ == "__main__":
    convert_all()

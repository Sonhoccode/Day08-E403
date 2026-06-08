"""Task 3: convert landing files to Markdown.

The project can run fully offline: DOCX files are extracted with python-docx,
PDF files with PyMuPDF, and MarkItDown is used only when explicitly enabled.
"""

import json
import os
from pathlib import Path

if os.getenv("USE_MARKITDOWN") == "1":
    try:
        from markitdown import MarkItDown
    except Exception:
        MarkItDown = None
else:
    MarkItDown = None

LANDING_DIR = Path(__file__).parent.parent / "data" / "landing"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "standardized"


def _extract_text(filepath: Path) -> str:
    if MarkItDown:
        return MarkItDown().convert(str(filepath)).text_content

    suffix = filepath.suffix.lower()
    if suffix == ".docx":
        from docx import Document

        document = Document(filepath)
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    if suffix == ".pdf":
        import fitz

        try:
            document = fitz.open(filepath)
            pages = [page.get_text().strip() for page in document]
            return "\n\n".join(page for page in pages if page)
        except Exception:
            return filepath.read_text(encoding="utf-8", errors="ignore")

    return filepath.read_text(encoding="utf-8", errors="ignore")


def convert_legal_docs() -> None:
    legal_dir = LANDING_DIR / "legal"
    output_dir = OUTPUT_DIR / "legal"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in legal_dir.iterdir():
        if filepath.suffix.lower() not in {".pdf", ".docx", ".doc"}:
            continue
        text = _extract_text(filepath)
        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(f"# {filepath.stem}\n\n{text}", encoding="utf-8")
        print(f"Saved: {output_path}")


def convert_news_articles() -> None:
    news_dir = LANDING_DIR / "news"
    output_dir = OUTPUT_DIR / "news"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filepath in news_dir.iterdir():
        if filepath.suffix.lower() != ".json":
            continue
        data = json.loads(filepath.read_text(encoding="utf-8"))
        header = (
            f"# {data.get('title', 'Unknown')}\n\n"
            f"**Source:** {data.get('url', 'N/A')}\n"
            f"**Crawled:** {data.get('date_crawled', 'N/A')}\n\n---\n\n"
        )
        output_path = output_dir / f"{filepath.stem}.md"
        output_path.write_text(header + data.get("content_markdown", ""), encoding="utf-8")
        print(f"Saved: {output_path}")


def convert_all() -> None:
    convert_legal_docs()
    convert_news_articles()


if __name__ == "__main__":
    convert_all()

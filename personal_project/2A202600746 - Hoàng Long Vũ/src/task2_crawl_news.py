"""Task 2: crawl real news articles and save them with metadata.

The crawler uses direct HTTP requests plus BeautifulSoup extraction because the
exercise environment does not always include Crawl4AI. It intentionally raises
an error when an article cannot be fetched/extracted instead of silently writing
mock data.
"""

from __future__ import annotations

import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://thanhnien.vn/ca-si-long-nhat-bi-bat-showbiz-viet-lien-tiep-chan-dong-vi-ma-tuy-18526052013032001.htm",
    "https://tienphong.vn/lien-tiep-nghe-si-dung-chat-cam-post1842599.tpo",
    "https://kenh14.vn/sao-viet-tieu-tan-su-nghiep-vi-lien-quan-den-ma-tuy-215260522111209355.chn",
    "https://vietnamnet.vn/sao-viet-bi-bat-ngoi-tu-mat-danh-tieng-vi-chat-cam-2513746.html",
    "https://nld.com.vn/showbiz-viet-nhung-nghe-si-gay-soc-vi-be-boi-ma-tuy-196250725113547841.htm",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
}

ARTICLE_SELECTORS = [
    ".detail-content",
    ".article__body",
    ".content-detail",
    ".article-body",
    ".detail__content",
    ".singular-content",
    ".cms-body",
    ".content-news-detail",
    "article",
]


def setup_directory() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _meta_content(soup: BeautifulSoup, *names: str) -> str:
    for name in names:
        tag = soup.find("meta", attrs={"property": name}) or soup.find("meta", attrs={"name": name})
        if tag and tag.get("content"):
            return _clean_text(tag["content"])
    return ""


def _extract_title(soup: BeautifulSoup) -> str:
    title = _meta_content(soup, "og:title", "twitter:title")
    if title:
        return title
    if soup.title and soup.title.string:
        return _clean_text(soup.title.string)
    h1 = soup.find("h1")
    return _clean_text(h1.get_text(" ", strip=True)) if h1 else "Untitled article"


def _extract_published_at(soup: BeautifulSoup) -> str:
    return _meta_content(
        soup,
        "article:published_time",
        "article:modified_time",
        "pubdate",
        "publishdate",
        "date",
    )


def _paragraphs_from_node(node) -> list[str]:
    paragraphs: list[str] = []
    for tag in node.find_all(["p", "h2", "h3", "li"]):
        for noisy in tag.select("script, style, iframe, figure, .VCSortableInPreviewMode"):
            noisy.decompose()
        text = _clean_text(tag.get_text(" ", strip=True))
        if len(text) >= 35 and text not in paragraphs:
            paragraphs.append(text)
    return paragraphs


def _extract_article_paragraphs(soup: BeautifulSoup) -> list[str]:
    best: list[str] = []
    for selector in ARTICLE_SELECTORS:
        paragraphs: list[str] = []
        for node in soup.select(selector):
            paragraphs.extend(_paragraphs_from_node(node))
        if len("\n".join(paragraphs)) > len("\n".join(best)):
            best = paragraphs

    if not best:
        best = [
            _clean_text(p.get_text(" ", strip=True))
            for p in soup.find_all("p")
            if len(_clean_text(p.get_text(" ", strip=True))) >= 35
        ]
    return best


def _to_markdown(title: str, paragraphs: list[str], url: str) -> str:
    body = "\n\n".join(paragraphs)
    return f"# {title}\n\n**Source:** {url}\n\n{body}\n"


def _source_name(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host.removeprefix("www.")


def fetch_article(url: str) -> dict:
    clean_url = url.strip()
    response = requests.get(clean_url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    for noisy in soup.select("script, style, noscript, iframe"):
        noisy.decompose()

    title = _extract_title(soup)
    paragraphs = _extract_article_paragraphs(soup)
    content_markdown = _to_markdown(title, paragraphs, clean_url)

    if len(content_markdown) < 500:
        raise ValueError(f"Extracted content is too short for {clean_url}")

    return {
        "url": clean_url,
        "source_name": _source_name(clean_url),
        "title": title,
        "published_at": _extract_published_at(soup),
        "date_crawled": datetime.now(timezone.utc).isoformat(),
        "http_status": response.status_code,
        "content_markdown": content_markdown,
    }


async def crawl_article(url: str) -> dict:
    return await asyncio.to_thread(fetch_article, url)


async def crawl_all() -> None:
    setup_directory()
    for i, url in enumerate(ARTICLE_URLS, 1):
        article = await crawl_article(url)
        filepath = DATA_DIR / f"article_{i:02d}.json"
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved: {filepath} <- {article['title']}")


if __name__ == "__main__":
    asyncio.run(crawl_all())

import os
import json
import asyncio
from datetime import datetime

from crawl4ai import AsyncWebCrawler

OUTPUT_DIR = "data/landing/news"

ARTICLE_URLS = [
    "https://znews.vn/tu-vu-viec-miu-le-rapper-mr-nhan-vi-sao-gioi-rapper-nghe-si-de-tim-den-chat-kich-thich-post1654009.html",

]


async def crawl_article(crawler, url, idx):
    result = await crawler.arun(url=url)

    if not result.success:
        print(f"Failed: {url}")
        return

    title = None

    if result.metadata:
        title = (
            result.metadata.get("title")
            or result.metadata.get("og:title")
        )

    if not title:
        title = f"article_{idx}"

    article_data = {
        "title": title,
        "source_url": url,
        "crawl_date": datetime.now().isoformat(),

        # nội dung
        "markdown": str(result.markdown),

        # html gốc
        "html": result.html
    }

    output_file = os.path.join(
        OUTPUT_DIR,
        f"article_{idx}.json"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            article_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"Saved: {output_file}")


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with AsyncWebCrawler() as crawler:
        for idx, url in enumerate(ARTICLE_URLS, start=1):
            await crawl_article(crawler, url, idx)


if __name__ == "__main__":
    asyncio.run(main())
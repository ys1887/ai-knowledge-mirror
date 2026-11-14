from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ekikyo_md_downloader import (
    crawl_category_pages,
    extract_category_page_urls,
    extract_title_and_markdown,
    unique_output_path,
)


CATEGORY_PAGE_1 = """
<html>
  <body>
    <main>
      <a href="https://ekikyo.jp/archives/111">外部ではない記事1</a>
      <a href="/archives/222">記事2</a>
      <a href="https://ekikyo.jp/archives/category/other">他カテゴリ</a>
      <a href="https://ekikyo.jp/archives/category/takashimaekidan/page/2">2</a>
    </main>
    <aside>
      <a href="https://ekikyo.jp/archives/category/other/page/2">別カテゴリページ</a>
    </aside>
  </body>
</html>
"""


CATEGORY_PAGE_2 = """
<html>
  <body>
    <main>
      <a href="https://ekikyo.jp/archives/333">記事3</a>
      <a href="/archives/222">記事2重複</a>
      <a href="https://ekikyo.jp/archives/category/takashimaekidan/page/3">3</a>
    </main>
  </body>
</html>
"""


CATEGORY_PAGE_3 = """
<html>
  <body>
    <main>
      <a href="https://ekikyo.jp/archives/444">記事4</a>
    </main>
  </body>
</html>
"""


ARTICLE_PAGE = """
<html>
  <head>
    <title>記事タイトル | わかりやすい易経・易占講座</title>
    <meta property="og:title" content="記事タイトル">
  </head>
  <body>
    <article class="post">
      <header><h1>記事タイトル</h1></header>
      <div class="entry-content">
        <p>本文の一段落目です。</p>
        <p>本文の二段落目です。</p>
        <div class="related">関連記事</div>
      </div>
    </article>
    <footer>フッター</footer>
  </body>
</html>
"""


class DummyResponse:
    def __init__(self, text: str) -> None:
        self.text = text
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"

    def raise_for_status(self) -> None:
        return None


class DummySession:
    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

    def get(self, url: str, timeout: int = 30) -> DummyResponse:  # noqa: ARG002
        return DummyResponse(self.mapping[url])


class EkikyoDownloaderTest(unittest.TestCase):
    def test_extract_category_page_urls_only_keeps_articles(self) -> None:
        urls, next_page = extract_category_page_urls(
            CATEGORY_PAGE_1,
            "https://ekikyo.jp/archives/category/takashimaekidan",
        )
        self.assertEqual(
            urls,
            [
                "https://ekikyo.jp/archives/111",
                "https://ekikyo.jp/archives/222",
            ],
        )
        self.assertEqual(next_page, "https://ekikyo.jp/archives/category/takashimaekidan/page/2")

    def test_crawl_category_pages_follows_pagination_and_deduplicates_articles(self) -> None:
        session = DummySession(
            {
                "https://ekikyo.jp/archives/category/takashimaekidan": CATEGORY_PAGE_1,
                "https://ekikyo.jp/archives/category/takashimaekidan/page/2": CATEGORY_PAGE_2,
                "https://ekikyo.jp/archives/category/takashimaekidan/page/3": CATEGORY_PAGE_3,
            }
        )
        crawl = crawl_category_pages("https://ekikyo.jp/archives/category/takashimaekidan", session, max_pages=10)
        self.assertEqual(
            crawl.article_urls,
            [
                "https://ekikyo.jp/archives/111",
                "https://ekikyo.jp/archives/222",
                "https://ekikyo.jp/archives/333",
                "https://ekikyo.jp/archives/444",
            ],
        )

    def test_extract_title_and_markdown_removes_noise(self) -> None:
        title, body = extract_title_and_markdown(ARTICLE_PAGE, "https://ekikyo.jp/archives/3695")
        self.assertEqual(title, "記事タイトル")
        self.assertIn("本文の一段落目です。", body)
        self.assertIn("本文の二段落目です。", body)
        self.assertNotIn("関連記事", body)
        self.assertNotIn("フッター", body)

    def test_unique_output_path_uses_suffix_for_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "記事.md").write_text("x", encoding="utf-8")
            self.assertEqual(unique_output_path(out, "記事").name, "記事-2.md")


if __name__ == "__main__":
    unittest.main()

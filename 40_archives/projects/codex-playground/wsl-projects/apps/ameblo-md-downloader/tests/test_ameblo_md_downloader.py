from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ameblo_md_downloader import (
    CrawlResult,
    crawl_theme_pages,
    extract_theme_page_urls,
    extract_title_and_markdown,
    unique_output_path,
)


THEME_PAGE_1 = """
<html>
  <body>
    <div class="theme-links">
      <a href="https://ameblo.jp/kokorokeiei/theme-100.html">他カテゴリ</a>
      <a href="/kokorokeiei/entry-11111111111.html">記事A</a>
      <a href="/kokorokeiei/entry-22222222222.html">記事B</a>
      <a href="/kokorokeiei/theme-10085932248.html?page=2">次ページ &gt;&gt;</a>
    </div>
  </body>
</html>
"""


THEME_PAGE_2 = """
<html>
  <body>
    <div class="theme-links">
      <a href="https://ameblo.jp/kokorokeiei/theme-200.html">他カテゴリ</a>
      <a href="/kokorokeiei/entry-33333333333.html">記事C</a>
      <a href="/kokorokeiei/entry-22222222222.html">記事B重複</a>
    </div>
  </body>
</html>
"""


ARTICLE_PAGE = """
<html>
  <head>
    <title>記事タイトル - Ameba</title>
    <meta property="og:title" content="記事タイトル">
  </head>
  <body>
    <header>ヘッダー</header>
    <aside>サイドバー</aside>
    <article id="main-entry" class="entry-body">
      <h1>記事タイトル</h1>
      <p>本文の一段落目です。</p>
      <p>本文の二段落目です。</p>
      <nav>記事内ナビ</nav>
      <div class="related">関連記事</div>
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


class AmebloDownloaderTest(unittest.TestCase):
    def test_extract_theme_page_urls_only_keeps_articles(self) -> None:
        urls, next_page = extract_theme_page_urls(THEME_PAGE_1, "https://ameblo.jp/kokorokeiei/theme-10085932248.html")
        self.assertEqual(
            urls,
            [
                "https://ameblo.jp/kokorokeiei/entry-11111111111.html",
                "https://ameblo.jp/kokorokeiei/entry-22222222222.html",
            ],
        )
        self.assertEqual(next_page, "https://ameblo.jp/kokorokeiei/theme-10085932248.html?page=2")

    def test_crawl_theme_pages_follows_pagination_and_deduplicates_articles(self) -> None:
        session = DummySession(
            {
                "https://ameblo.jp/kokorokeiei/theme-10085932248.html": THEME_PAGE_1,
                "https://ameblo.jp/kokorokeiei/theme-10085932248.html?page=2": THEME_PAGE_2,
            }
        )
        crawl = crawl_theme_pages("https://ameblo.jp/kokorokeiei/theme-10085932248.html", session, max_pages=10)
        self.assertEqual(
            crawl.article_urls,
            [
                "https://ameblo.jp/kokorokeiei/entry-11111111111.html",
                "https://ameblo.jp/kokorokeiei/entry-22222222222.html",
                "https://ameblo.jp/kokorokeiei/entry-33333333333.html",
            ],
        )

    def test_extract_title_and_markdown_removes_noise(self) -> None:
        title, body = extract_title_and_markdown(ARTICLE_PAGE, "https://ameblo.jp/kokorokeiei/entry-11111111111.html")
        self.assertEqual(title, "記事タイトル")
        self.assertIn("本文の一段落目です。", body)
        self.assertIn("本文の二段落目です。", body)
        self.assertNotIn("ヘッダー", body)
        self.assertNotIn("サイドバー", body)
        self.assertNotIn("関連記事", body)

    def test_unique_output_path_uses_suffix_for_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / "記事.md").write_text("x", encoding="utf-8")
            path = unique_output_path(out, "記事")
            self.assertEqual(path.name, "記事-2.md")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Download Ameblo theme articles and save them as markdown files.

The crawler only follows article URLs and the theme page pagination link.
It ignores category links and other navigation links on the page.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


ARTICLE_URL_RE = re.compile(r"^https?://[^/]+/[^/]+/entry-\d+\.html(?:[?#].*)?$")
BAD_FILENAME_CHARS = r'<>:"/\|?*'
NOISE_TAGS = {
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "aside",
    "form",
    "button",
    "input",
    "svg",
}
BLOCK_TAGS = {
    "article",
    "section",
    "div",
    "p",
    "ul",
    "ol",
    "li",
    "pre",
    "blockquote",
    "table",
    "thead",
    "tbody",
    "tr",
    "td",
    "th",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
}


@dataclass(frozen=True)
class CrawlResult:
    article_urls: list[str]
    pages_visited: int


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def sanitize_filename(name: str) -> str:
    cleaned = name.strip()
    for char in BAD_FILENAME_CHARS:
        cleaned = cleaned.replace(char, "-")
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.rstrip(". ")
    return cleaned[:180] or "article"


def unique_output_path(output_dir: Path, base_name: str) -> Path:
    candidate = output_dir / f"{base_name}.md"
    if not candidate.exists():
        return candidate

    index = 2
    while True:
        candidate = output_dir / f"{base_name}-{index}.md"
        if not candidate.exists():
            return candidate
        index += 1


def is_article_url(url: str) -> bool:
    return bool(ARTICLE_URL_RE.match(url))


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        }
    )
    return session


def fetch_html(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = response.encoding or response.apparent_encoding
    return response.text


def extract_theme_page_urls(html: str, base_url: str) -> tuple[list[str], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    article_urls: list[str] = []
    seen: set[str] = set()
    next_page_url: str | None = None

    for anchor in soup.find_all("a", href=True):
        href = urljoin(base_url, anchor["href"])
        label = normalize_whitespace(anchor.get_text(" ", strip=True))

        if is_article_url(href):
            if href not in seen:
                seen.add(href)
                article_urls.append(href)
            continue

        if next_page_url is None and is_next_page_link(anchor, label):
            next_page_url = href

    return article_urls, next_page_url


def is_next_page_link(anchor: Tag, label: str) -> bool:
    if not label:
        return False

    lowered = label.lower()
    if "次ページ" in label or "次へ" in label:
        return True
    if lowered in {"next", "next page"}:
        return True

    rel = anchor.get("rel")
    if rel and any(part.lower() == "next" for part in rel):
        return True

    href = anchor.get("href", "")
    return bool(re.search(r"(?:[?&]page=\d+|/page-\d+)", href))


def crawl_theme_pages(start_url: str, session: requests.Session, max_pages: int = 200) -> CrawlResult:
    visited_pages: set[str] = set()
    seen_articles: set[str] = set()
    article_urls: list[str] = []

    current_url: str | None = start_url
    pages_visited = 0

    while current_url and current_url not in visited_pages:
        if pages_visited >= max_pages:
            break

        visited_pages.add(current_url)
        pages_visited += 1
        html = fetch_html(session, current_url)
        page_articles, next_page_url = extract_theme_page_urls(html, current_url)

        for article_url in page_articles:
            if article_url not in seen_articles:
                seen_articles.add(article_url)
                article_urls.append(article_url)

        current_url = next_page_url

    return CrawlResult(article_urls=article_urls, pages_visited=pages_visited)


def choose_content_node(soup: BeautifulSoup) -> Tag:
    candidates: list[Tag] = []
    for tag in soup.find_all(BLOCK_TAGS):
        if not isinstance(tag, Tag):
            continue
        if not tag.get_text(" ", strip=True):
            continue
        candidates.append(tag)

    if not candidates:
        return soup.body or soup

    def score(node: Tag) -> tuple[int, int]:
        text = normalize_whitespace(node.get_text(" ", strip=True))
        length = len(text)
        link_text = sum(len(normalize_whitespace(a.get_text(" ", strip=True))) for a in node.find_all("a"))
        class_id = " ".join(
            filter(
                None,
                [
                    " ".join(node.get("class", [])) if isinstance(node.get("class"), list) else None,
                    node.get("id", ""),
                ],
            )
        ).lower()
        bonus = 0
        for token in ("article", "entry", "contents", "main", "text", "body", "post"):
            if token in class_id:
                bonus += 2000
        for token in ("nav", "menu", "footer", "header", "side", "related", "comment", "share", "sns"):
            if token in class_id:
                bonus -= 2000
        return (length - link_text + bonus, length)

    return max(candidates, key=score)


def prune_noise(node: Tag) -> None:
    for tag in list(node.find_all(True)):
        if tag.name in NOISE_TAGS:
            tag.decompose()
            continue
        class_id = " ".join(
            filter(
                None,
                [
                    " ".join(tag.get("class", [])) if isinstance(tag.get("class"), list) else None,
                    tag.get("id", ""),
                ],
            )
        ).lower()
        if any(token in class_id for token in ("comment", "related", "breadcrumb", "pager", "theme", "share", "sns")):
            tag.decompose()


def render_inline_text(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return str(node)

    if node.name == "br":
        return "\n"

    if node.name in {"img", "svg"}:
        return ""

    if node.name == "a":
        return node.get_text(" ", strip=True)

    parts = [render_inline_text(child) for child in node.children]
    return "".join(parts)


def render_markdown(node: Tag) -> str:
    lines: list[str] = []

    def emit_block(text: str = "") -> None:
        if text == "":
            if lines and lines[-1] == "":
                return
            lines.append("")
            return
        lines.append(text)

    def walk(current: Tag | NavigableString) -> None:
        if isinstance(current, NavigableString):
            text = normalize_whitespace(str(current))
            if text:
                emit_block(text)
            return

        if current.name in NOISE_TAGS:
            return

        if current.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(current.name[1])
            text = normalize_whitespace(render_inline_text(current))
            if text:
                emit_block("#" * level + f" {text}")
                emit_block()
            return

        if current.name == "li":
            text = normalize_whitespace(render_inline_text(current))
            if text:
                emit_block(f"- {text}")
            return

        if current.name == "blockquote":
            text = normalize_whitespace(render_inline_text(current))
            if text:
                for part in text.splitlines():
                    emit_block(f"> {part.strip()}")
                emit_block()
            return

        if current.name == "pre":
            text = current.get_text("\n", strip=False).rstrip("\n")
            if text:
                emit_block("```")
                for part in text.splitlines():
                    lines.append(part.rstrip())
                emit_block("```")
                emit_block()
            return

        is_block = current.name in BLOCK_TAGS
        if is_block:
            before = len(lines)
            for child in current.children:
                walk(child)
            if len(lines) > before:
                emit_block()
            return

        for child in current.children:
            walk(child)

    walk(node)

    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_title_and_markdown(html: str, url: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    for selector in (
        ("meta", {"property": "og:title"}),
        ("meta", {"name": "title"}),
    ):
        tag = soup.find(selector[0], selector[1])
        if tag and tag.get("content"):
            title = normalize_whitespace(tag["content"])
            break

    if not title and soup.title and soup.title.string:
        title = normalize_whitespace(soup.title.string)

    if not title:
        h1 = soup.find("h1")
        if h1:
            title = normalize_whitespace(h1.get_text(" ", strip=True))

    if not title:
        parsed = urlparse(url)
        title = parsed.path.rsplit("/", 1)[-1].replace(".html", "") or "article"

    content_node = choose_content_node(soup)
    prune_noise(content_node)
    for heading in list(content_node.find_all("h1")):
        heading_text = normalize_whitespace(heading.get_text(" ", strip=True))
        if heading_text and heading_text == title:
            heading.decompose()
    body = render_markdown(content_node)

    return title, body


def write_article(output_dir: Path, title: str, body: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = sanitize_filename(title)
    path = unique_output_path(output_dir, base_name)
    content = f"# {title}\n\n{body}\n"
    path.write_text(content, encoding="utf-8")
    return path


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download articles from an Ameblo theme page and save them as markdown files."
    )
    parser.add_argument("--url", required=True, help="Theme page URL.")
    parser.add_argument(
        "--out",
        required=True,
        type=Path,
        help="Output directory for markdown files.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print collected article URLs without downloading them.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=200,
        help="Safety limit for theme pagination.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    output_dir: Path = args.out
    output_dir.mkdir(parents=True, exist_ok=True)

    session = make_session()
    crawl = crawl_theme_pages(args.url, session, max_pages=args.max_pages)

    if args.dry_run:
        for article_url in crawl.article_urls:
            print(article_url)
        return 0

    for article_url in crawl.article_urls:
        try:
            html = fetch_html(session, article_url)
            title, body = extract_title_and_markdown(html, article_url)
            path = write_article(output_dir, title, body)
            print(f"saved {path}")
        except Exception as exc:  # pragma: no cover - surface the failing URL to the user
            raise RuntimeError(f"failed to process {article_url}: {exc}") from exc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


FRONTMATTER = """---
title: "易経 本卦引用 AI ソース"
hexagram_count: 64
format: "ai-source-minimal"
---
"""

SOURCE_FILE_RE = re.compile(r"^(?P<number>\d{2})_(?P<name>.+)\.md$")
TITLE_RE = re.compile(r"^title:\s*(?P<title>.+?)\s*$")
LEVEL2_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
HONKA_MARKERS = ("（占）", "(占)")
LINE_TITLES = {
    "初九",
    "九二",
    "九三",
    "九四",
    "九五",
    "上九",
    "初六",
    "六二",
    "六三",
    "六四",
    "六五",
    "上六",
    "用九",
    "用六",
}


class ExtractionError(Exception):
    pass


@dataclass(frozen=True)
class HexagramDocument:
    number: int
    title: str
    honka_uranai_lines: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an honka markdown containing only honka (占) sections."
    )
    parser.add_argument(
        "--source-dir",
        default="/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/140_高島易断/141_高島易断",
        help="Directory containing the 64 Takashima source markdown files.",
    )
    parser.add_argument(
        "--output",
        default="/home/ys/projects/ekikyo/work/honka.md",
        help="Output markdown path.",
    )
    return parser.parse_args()


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if value[:1] in {'"', "'"} and value[-1:] == value[:1]:
        return value[1:-1]
    return value


def _trim_blank_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and lines[start].strip() == "":
        start += 1
    while end > start and lines[end - 1].strip() == "":
        end -= 1
    return lines[start:end]


def _body_start(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return index + 1
    raise ExtractionError("frontmatter closing delimiter not found")


def _extract_title(lines: list[str], path: Path) -> str:
    if not lines or lines[0].strip() != "---":
        raise ExtractionError(f"frontmatter not found: {path}")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        match = TITLE_RE.match(line)
        if match:
            return _strip_quotes(match.group("title"))
    raise ExtractionError(f"title not found: {path}")


def _find_top_heading(lines: list[str], start: int, path: Path) -> int:
    for index in range(start, len(lines)):
        if lines[index].startswith("# "):
            return index
    raise ExtractionError(f"top heading not found: {path}")


def _find_first_line_heading_index(lines: list[str], start: int) -> int | None:
    for index in range(start, len(lines)):
        match = LEVEL2_RE.match(lines[index])
        if match and match.group("title") in LINE_TITLES:
            return index
    return None


def _extract_honka_uranai_lines(lines: list[str], top_heading_index: int, title: str) -> list[str]:
    start = top_heading_index + 1
    while start < len(lines) and lines[start].strip() == "":
        start += 1
    if start < len(lines) and lines[start].strip() == title:
        start += 1
    first_line_heading_index = _find_first_line_heading_index(lines, start)
    end = first_line_heading_index if first_line_heading_index is not None else len(lines)
    marker_index = None
    for index in range(start, end):
        if any(lines[index].startswith(marker) for marker in HONKA_MARKERS):
            marker_index = index
            break
    if marker_index is None:
        raise ExtractionError(f"honka 占 section not found before first line heading: {title}")
    return _trim_blank_edges(lines[marker_index:end])


def load_documents(source_dir: Path) -> list[HexagramDocument]:
    if not source_dir.is_dir():
        raise ExtractionError(f"source directory not found: {source_dir}")
    paths = [path for path in source_dir.glob("*.md") if SOURCE_FILE_RE.match(path.name)]
    documents: list[HexagramDocument] = []
    for path in sorted(paths, key=lambda current: int(SOURCE_FILE_RE.match(current.name).group("number"))):  # type: ignore[union-attr]
        match = SOURCE_FILE_RE.match(path.name)
        if match is None:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        title = _extract_title(lines, path)
        body_start = _body_start(lines)
        top_heading_index = _find_top_heading(lines, body_start, path)
        documents.append(
            HexagramDocument(
                number=int(match.group("number")),
                title=title,
                honka_uranai_lines=_extract_honka_uranai_lines(lines, top_heading_index, title),
            )
        )
    if len(documents) != 64:
        raise ExtractionError(f"expected 64 source files, found {len(documents)}")
    return documents


def build_output(documents: list[HexagramDocument]) -> str:
    lines: list[str] = [FRONTMATTER.rstrip(), ""]
    for document in documents:
        lines.append(f"## {document.number} {document.title}")
        lines.append("")
        lines.extend(document.honka_uranai_lines)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    documents = load_documents(Path(args.source_dir))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_output(documents), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

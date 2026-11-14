#!/usr/bin/env python3
"""Render the 64卦 Markdown into a Word-compatible RTF document.

The source format is Markdown with a simple, stable structure:
- YAML front matter at the top.
- `## NN.卦名` marks a chapter boundary.
- The next plain line is the chapter title text.
- `### 初九` etc. are subsection titles.
- Lines beginning with `>` are bold quote/paraphrase lines.
- All other non-empty lines are body paragraphs and get a leading ideographic
  space.

This keeps the document editable in Word and Ichitaro without introducing any
new dependencies.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


FONT_NAME = "Noto Sans JP"
BODY_SIZE = 32  # 16pt
SUBTITLE_SIZE = 36  # 18pt
TITLE_SIZE = 40  # 20pt


KANJI_NUMERALS = {
    0: "〇",
    1: "一",
    2: "二",
    3: "三",
    4: "四",
    5: "五",
    6: "六",
    7: "七",
    8: "八",
    9: "九",
}


def kanji_number(value: int) -> str:
    if value <= 0:
        raise ValueError(f"chapter number must be positive: {value}")
    if value < 10:
        return KANJI_NUMERALS[value]
    if value == 10:
        return "十"
    if value < 20:
        return "十" + KANJI_NUMERALS[value - 10]
    if value < 100:
        tens, ones = divmod(value, 10)
        prefix = KANJI_NUMERALS[tens] + "十"
        return prefix if ones == 0 else prefix + KANJI_NUMERALS[ones]
    raise ValueError(f"chapter number out of range: {value}")


def escape_rtf_text(text: str) -> str:
    """Escape text for RTF while keeping Japanese readable via CP932 bytes."""

    parts: list[str] = []
    for ch in text:
        if ch == "\\":
            parts.append(r"\\")
            continue
        if ch == "{":
            parts.append(r"\{")
            continue
        if ch == "}":
            parts.append(r"\}")
            continue

        try:
            encoded = ch.encode("cp932", errors="strict")
        except UnicodeEncodeError:
            codepoint = ord(ch)
            signed = codepoint if codepoint < 0x8000 else codepoint - 0x10000
            parts.append(f"\\u{signed}?")
            continue

        if len(encoded) == 1 and encoded[0] < 0x80:
            parts.append(chr(encoded[0]))
            continue

        parts.extend(f"\\'{byte:02x}" for byte in encoded)

    return "".join(parts)


def parse_markdown(path: Path) -> list[tuple[str, str]]:
    """Parse the book Markdown into typed renderable blocks."""

    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: list[tuple[str, str]] = []

    in_front_matter = False
    chapter_number: int | None = None
    chapter_title_emitted = False

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if line == "---":
            in_front_matter = not in_front_matter
            continue
        if in_front_matter:
            continue

        if not stripped:
            continue

        chapter_match = re.match(r"^##\s+(\d+)\.(.+?)\s*$", stripped)
        if chapter_match:
            chapter_number = int(chapter_match.group(1))
            chapter_title_emitted = False
            continue

        subtitle_match = re.match(r"^###\s+(.+?)\s*$", stripped)
        if subtitle_match:
            blocks.append(("subtitle", subtitle_match.group(1)))
            continue

        if stripped.startswith(">"):
            quote = stripped[1:].lstrip()
            blocks.append(("quote", quote))
            continue

        if chapter_number is not None and not chapter_title_emitted:
            title = f"{kanji_number(chapter_number)}\u3000{stripped}"
            blocks.append(("title", title))
            chapter_title_emitted = True
            continue

        blocks.append(("body", stripped))

    return blocks


def render_paragraph(kind: str, text: str) -> str:
    if kind == "title":
        size = TITLE_SIZE
        bold = True
        prefix = r"\qj"
        leading_space = False
    elif kind == "subtitle":
        size = SUBTITLE_SIZE
        bold = True
        prefix = r"\qj"
        leading_space = False
    elif kind == "quote":
        size = BODY_SIZE
        bold = True
        prefix = r"\qj"
        leading_space = False
    else:
        size = BODY_SIZE
        bold = False
        prefix = r"\qj"
        leading_space = True

    content = ("\u3000" + text) if leading_space else text
    escaped = escape_rtf_text(content)
    bold_open = r"\b" if bold else ""
    bold_close = r"\b0" if bold else ""
    return (
        "{"
        + rf"\pard\plain\f0\fs{size}{prefix}\sb0\sa0\sl0\slmult0"
        + bold_open
        + " "
        + escaped
        + bold_close
        + r"\par"
        + "}"
    )


def render_rtf(blocks: list[tuple[str, str]]) -> str:
    font_table = (
        r"{\fonttbl"
        rf"{{\f0\fnil\fcharset128 {FONT_NAME};}}"
        "}"
    )
    header = (
        r"{\rtf1\ansi\ansicpg932\uc1\deff0"
        + font_table
        + r"{\colortbl;\red0\green0\blue0;}"
        + r"\paperw11906\paperh16838"
        + r"\margt56\margb56\margl566\margr1134"
        + r"\viewkind1\viewscale110"
        + r"\sectd\vertsect\stextflow1"
        + "\n"
    )
    body = "\n".join(render_paragraph(kind, text) for kind, text in blocks)
    return header + body + "\n}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render 64卦 Markdown to a Word-compatible RTF document."
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="src/book_6/64卦_暗喩用.md",
        help="Input Markdown file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="build/易経.doc",
        help="Output RTF/.doc file.",
    )
    args = parser.parse_args()

    source = Path(args.input)
    output = Path(args.output)
    blocks = parse_markdown(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_rtf(blocks), encoding="cp932", errors="strict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

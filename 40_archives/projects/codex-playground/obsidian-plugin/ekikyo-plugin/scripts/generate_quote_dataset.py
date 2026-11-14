from __future__ import annotations

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
BODY_EXCERPT_SOURCE = REPO_ROOT / "vendor" / "ekikyo" / "assets" / "本文抜粋.md"
DIVINATION_EXCERPT_SOURCE = REPO_ROOT / "vendor" / "ekikyo" / "assets" / "占断抜粋.md"
TAKASHIMA_SOURCE_DIR = REPO_ROOT / "vendor" / "ekikyo" / "assets" / "takashima"
REFERENCE_CASES_SOURCE = REPO_ROOT / "vendor" / "ekikyo" / "assets" / "高島易断占例.md"
HEXAGRAM_MAP_SOURCE = REPO_ROOT / "reference" / "iching-calculator" / "base_hexagrams.json"
OUTPUT_PATH = REPO_ROOT / "data" / "quote-dataset.json"

HEXAGRAM_HEADING_RE = re.compile(r"^##\s+(?P<number>\d+)\s+(?P<title>.+)$", re.MULTILINE)
LINE_HEADING_RE = re.compile(
    r"^###\s+(?P<title>本卦|初爻|[2-5]爻|[二三四五]爻|上爻|用爻|初九|初六|[六九][二三四五]|上九|上六)\s*$",
    re.MULTILINE,
)

LINE_LABEL_TO_NUMBER = {
    "初爻": 1,
    "初九": 1,
    "初六": 1,
    "2爻": 2,
    "二爻": 2,
    "九二": 2,
    "六二": 2,
    "3爻": 3,
    "三爻": 3,
    "九三": 3,
    "六三": 3,
    "4爻": 4,
    "四爻": 4,
    "九四": 4,
    "六四": 4,
    "5爻": 5,
    "五爻": 5,
    "九五": 5,
    "六五": 5,
    "上爻": 6,
    "上九": 6,
    "上六": 6,
}
LINE_HEADING_CANDIDATES = {
    1: ("初爻", "初九", "初六"),
    2: ("二爻", "2爻", "九二", "六二"),
    3: ("三爻", "3爻", "九三", "六三"),
    4: ("四爻", "4爻", "九四", "六四"),
    5: ("五爻", "5爻", "九五", "六五"),
    6: ("上爻", "上九", "上六"),
}
TAKASHIMA_SECTION_HEADING_RE = re.compile(r"^####\s+(?P<title>.+)$", re.MULTILINE)
REFERENCE_CASE_ENTRY_HEADING_RE = re.compile(r"^#\s+(?P<number>\d{2})_(?P<title>.+?)$", re.MULTILINE)
REFERENCE_CASE_LINE_HEADING_RE = re.compile(
    r"^##\s+(?P<title>初爻|[2-5]爻|[二三四五]爻|上爻|用爻|初九|初六|[六九][二三四五]|上九|上六)\s*$",
    re.MULTILINE,
)


def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    first_non_empty = next((index for index, line in enumerate(lines) if line.strip()), None)
    if first_non_empty is None or lines[first_non_empty].strip() != "---":
        return text
    for index in range(first_non_empty + 1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip("\n")
    return text


def _heading_spans(text: str, pattern: re.Pattern[str]) -> list[tuple[re.Match[str], int, int]]:
    matches = list(pattern.finditer(text))
    spans: list[tuple[re.Match[str], int, int]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        spans.append((match, start, end))
    return spans


def _parse_hexagram_blocks(text: str) -> dict[int, tuple[str, str]]:
    stripped = _strip_frontmatter(text)
    blocks: dict[int, tuple[str, str]] = {}
    for match, start, end in _heading_spans(stripped, HEXAGRAM_HEADING_RE):
        blocks[int(match.group("number"))] = (match.group("title").strip(), stripped[start:end].strip())
    return blocks


def _parse_excerpt_blocks(text: str) -> dict[int, dict[str, object]]:
    raw_hexagrams = _parse_hexagram_blocks(text)
    parsed: dict[int, dict[str, object]] = {}
    for number, (_, hexagram_block) in raw_hexagrams.items():
        honka_block = ""
        line_blocks: dict[int, str] = {}
        for match, start, end in _heading_spans(hexagram_block, LINE_HEADING_RE):
            label = match.group("title")
            block = hexagram_block[start:end].strip()
            if label == "本卦":
                honka_block = block
                continue
            line_number = LINE_LABEL_TO_NUMBER.get(label)
            if line_number is None:
                continue
            line_blocks[line_number] = block
        parsed[number] = {
            "honka": honka_block,
            "lines": line_blocks,
        }
    return parsed


def _normalize_quote_block_spacing(block_text: str) -> str:
    normalized_lines: list[str] = []
    consecutive_quote_lines = 0

    for line in block_text.splitlines():
        stripped = line.strip()
        is_blank = stripped == ""
        is_quote = stripped.startswith(">")

        if not is_blank and not is_quote and consecutive_quote_lines >= 2:
            if normalized_lines and normalized_lines[-1] != "":
                normalized_lines.append("")

        normalized_lines.append(line)

        if is_quote:
            consecutive_quote_lines += 1
        else:
            consecutive_quote_lines = 0

    return "\n".join(normalized_lines)


def _load_hexagram_map() -> list[dict[str, object]]:
    payload = json.loads(HEXAGRAM_MAP_SOURCE.read_text(encoding="utf-8"))
    return payload["hexagrams"]


def _line_heading_candidates(line_label: str) -> tuple[str, ...]:
    if line_label == "用爻":
        return ("用爻",)
    line_number = LINE_LABEL_TO_NUMBER.get(line_label)
    if line_number is not None:
        return LINE_HEADING_CANDIDATES[line_number]
    return (line_label,)


def _extract_line_section(
    block_text: str,
    line_label: str,
    *,
    pattern: re.Pattern[str],
    error_prefix: str,
) -> tuple[str, str]:
    expected_titles = _line_heading_candidates(line_label)
    for match, start, end in _heading_spans(block_text, pattern):
        if match.group("title") in expected_titles:
            return match.group("title"), block_text[start:end].strip()
    raise ValueError(f"{error_prefix} not found: {line_label}")


def _extract_named_section(text: str, heading: str, level: int = 3) -> str:
    pattern = re.compile(r"^" + ("#" * level) + r"\s+" + re.escape(heading) + r"\s*$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        raise ValueError(f"section not found: {heading}")
    start = match.end()
    next_match = re.search(r"^" + ("#" * level) + r"\s+", text[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def _extract_subsection(block_text: str, heading: str) -> str:
    for match, start, end in _heading_spans(block_text, TAKASHIMA_SECTION_HEADING_RE):
        if match.group("title") == heading:
            return block_text[start:end].strip()
    raise ValueError(f"subsection not found: {heading}")


def _load_takashima_catalog() -> dict[int, Path]:
    catalog: dict[int, Path] = {}
    for path in sorted(TAKASHIMA_SOURCE_DIR.glob("*.md")):
        match = re.match(r"^(?P<number>0?[1-9][0-9]?)_.+\.md$", path.name)
        if match is None:
            continue
        catalog[int(match.group("number"))] = path
    return catalog


def _load_takashima_raw(path: Path, line_label: str) -> dict[str, str]:
    text = _strip_frontmatter(path.read_text(encoding="utf-8"))
    honka_block = _extract_named_section(text, "本卦解釈", level=3)
    line_block = _extract_named_section(text, "変爻解釈", level=3)

    _, line_text = _extract_line_section(
        line_block,
        line_label,
        pattern=TAKASHIMA_SECTION_HEADING_RE,
        error_prefix="takashima line",
    )
    line_heading, _ = _extract_line_section(
        line_block,
        line_label,
        pattern=TAKASHIMA_SECTION_HEADING_RE,
        error_prefix="takashima line",
    )

    return {
        "kaji": _extract_subsection(honka_block, "卦辞"),
        "tanden": _extract_subsection(honka_block, "彖伝"),
        "taisho": _extract_subsection(honka_block, "大象伝"),
        "lineHeading": line_heading,
        "lineText": line_text,
    }


def _extract_reference_case_entry(text: str, number: int) -> str | None:
    for match, start, end in _heading_spans(text, REFERENCE_CASE_ENTRY_HEADING_RE):
        if int(match.group("number")) == number:
            return text[start:end].strip()
    return None


def _load_reference_case_excerpt(number: int, line_label: str) -> str:
    text = REFERENCE_CASES_SOURCE.read_text(encoding="utf-8")
    entry = _extract_reference_case_entry(text, number)
    if entry is None:
        return ""

    sections: list[str] = []
    expected_titles = _line_heading_candidates(line_label)
    for match, start, end in _heading_spans(entry, REFERENCE_CASE_LINE_HEADING_RE):
        if match.group("title") not in expected_titles:
            continue
        section_text = entry[start:end].strip()
        if section_text:
            sections.append(section_text)
    if not sections:
        return ""
    return "\n\n".join(sections).rstrip()


def build_dataset() -> dict[str, object]:
    body_excerpt_text = BODY_EXCERPT_SOURCE.read_text(encoding="utf-8")
    divination_excerpt_text = DIVINATION_EXCERPT_SOURCE.read_text(encoding="utf-8")
    body_excerpt_blocks = _parse_excerpt_blocks(body_excerpt_text)
    divination_excerpt_blocks = _parse_excerpt_blocks(divination_excerpt_text)
    takashima_catalog = _load_takashima_catalog()

    hexagrams: list[dict[str, object]] = []
    for item in _load_hexagram_map():
        number = int(item["number"])
        if number not in takashima_catalog:
            raise ValueError(f"missing takashima file for hexagram {number}")
        if number not in body_excerpt_blocks:
            raise ValueError(f"missing body excerpt block for hexagram {number}")
        if number not in divination_excerpt_blocks:
            raise ValueError(f"missing divination excerpt block for hexagram {number}")

        body_excerpt = body_excerpt_blocks[number]
        divination_excerpt = divination_excerpt_blocks[number]
        body_excerpt_lines = body_excerpt["lines"]
        divination_excerpt_lines = divination_excerpt["lines"]
        missing_body_excerpt_lines = [line for line in range(1, 7) if line not in body_excerpt_lines]
        if not body_excerpt["honka"] or missing_body_excerpt_lines:
            raise ValueError(f"missing body excerpt blocks for hexagram {number}: {missing_body_excerpt_lines}")
        missing_divination_excerpt_lines = [line for line in range(1, 7) if line not in divination_excerpt_lines]
        if not divination_excerpt["honka"] or missing_divination_excerpt_lines:
            raise ValueError(f"missing divination excerpt blocks for hexagram {number}: {missing_divination_excerpt_lines}")

        takashima_lines: dict[str, dict[str, str]] = {}
        reference_case_excerpts: dict[str, str] = {}
        for line_number in range(1, 7):
            line_label = next(
                label for label, mapped_number in LINE_LABEL_TO_NUMBER.items() if mapped_number == line_number and label.endswith("爻")
            )
            takashima_raw = _load_takashima_raw(takashima_catalog[number], line_label)
            takashima_lines[str(line_number)] = takashima_raw
            reference_case_excerpts[str(line_number)] = _load_reference_case_excerpt(number, line_label)

        hexagrams.append(
            {
                "number": number,
                "name": item["name"],
                "binary": item["binary"],
                "bodyExcerpt": {
                    "honka": _normalize_quote_block_spacing(str(body_excerpt["honka"])),
                    "lines": {
                        str(line): _normalize_quote_block_spacing(str(body_excerpt_lines[line]))
                        for line in range(1, 7)
                    },
                },
                "divinationExcerpt": {
                    "honka": str(divination_excerpt["honka"]).strip(),
                    "lines": {
                        str(line): str(divination_excerpt_lines[line]).strip()
                        for line in range(1, 7)
                    },
                },
                "takashima": {
                    "kaji": takashima_lines["1"]["kaji"],
                    "tanden": takashima_lines["1"]["tanden"],
                    "taisho": takashima_lines["1"]["taisho"],
                    "lines": {
                        str(line): {
                            "heading": takashima_lines[str(line)]["lineHeading"],
                            "text": takashima_lines[str(line)]["lineText"],
                        }
                        for line in range(1, 7)
                    },
                },
                "referenceCases": reference_case_excerpts,
            }
        )

    return {"hexagrams": hexagrams}


def main() -> int:
    dataset = build_dataset()
    OUTPUT_PATH.write_text(
        json.dumps(dataset, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(OUTPUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

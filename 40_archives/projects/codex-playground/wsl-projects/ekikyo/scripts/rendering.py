from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from profiles import ValidationError, canonical_quotes_root, repo_root


HEXAGRAM_HEADING_RE = re.compile(r"^##\s+(?P<number>\d+)\s+(?P<title>.+)$", re.MULTILINE)
SECTION_HEADING_RE = re.compile(r"^####\s+(?P<title>.+)$", re.MULTILINE)
LINE_HEADING_RE = re.compile(
    r"^###\s+(?P<title>初爻|[2-5]爻|[二三四五]爻|上爻|用爻|初九|初六|[六九][二三四五]|上九|上六)\s*$",
    re.MULTILINE,
)
TAKASHIMA_SOURCE_FILE_RE = re.compile(r"^(?P<number>0?[1-9][0-9]?)_.+\.md$")
LINE_LABEL_TO_NUMBER = {
    "初爻": 1,
    "2爻": 2,
    "二爻": 2,
    "3爻": 3,
    "三爻": 3,
    "4爻": 4,
    "四爻": 4,
    "5爻": 5,
    "五爻": 5,
    "上爻": 6,
}
LINE_HEADING_CANDIDATES = {
    1: ("初爻", "初九", "初六"),
    2: ("二爻", "2爻", "九二", "六二"),
    3: ("三爻", "3爻", "九三", "六三"),
    4: ("四爻", "4爻", "九四", "六四"),
    5: ("五爻", "5爻", "九五", "六五"),
    6: ("上爻", "上九", "上六"),
}
KANJI_LINE_LABELS = {
    "初爻": "初爻",
    "2爻": "二爻",
    "二爻": "二爻",
    "3爻": "三爻",
    "三爻": "三爻",
    "4爻": "四爻",
    "四爻": "四爻",
    "5爻": "五爻",
    "五爻": "五爻",
    "上爻": "上爻",
}
GENERIC_LINE_TITLES = frozenset((*LINE_LABEL_TO_NUMBER.keys(), "用爻"))

REFERENCE_CASES_PATH = repo_root() / "assets" / "高島易断占例.md"
REFERENCE_CASE_HEADING_RE = re.compile(r"^#\s+(?P<number>\d{2})_(?P<title>.+?)(?:\s+占例抜粋)?$", re.MULTILINE)
REFERENCE_CASE_SECTION_HEADING_RE = re.compile(r"^##\s+(?P<title>.+)$", re.MULTILINE)



@dataclass(frozen=True)
class QuoteBlock:
    original: str
    reading: str


@dataclass(frozen=True)
class HexagramQuotes:
    number: int
    title: str
    raw_text: str
    kaji: QuoteBlock
    tanden: QuoteBlock
    taisho: QuoteBlock


@dataclass(frozen=True)
class LineQuotes:
    line_label: str
    raw_text: str
    koji: QuoteBlock
    shozoden: QuoteBlock | None


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"missing source file: {path}")
    return path.read_text(encoding="utf-8")


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


def _extract_hexagram_entry(text: str, number: int) -> tuple[str, str]:
    for match, start, end in _heading_spans(text, HEXAGRAM_HEADING_RE):
        if int(match.group("number")) == number:
            return match.group("title").strip(), text[start:end].strip()
    raise ValidationError(f"hexagram {number} not found in quote source")


def _extract_section(block_text: str, heading: str) -> str:
    for match, start, end in _heading_spans(block_text, SECTION_HEADING_RE):
        if match.group("title") == heading:
            return block_text[start:end].strip()
    raise ValidationError(f"section not found: {heading}")


def _collect_quote_blocks(block_text: str) -> list[QuoteBlock]:
    blocks: list[QuoteBlock] = []
    for group in _quote_line_groups(block_text):
        blocks.append(_split_quote_block("\n".join(group)))
    return blocks


def _quote_line_groups(block_text: str) -> list[list[str]]:
    groups: list[list[str]] = []
    current_group: list[str] = []
    for line in block_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            current_group.append(stripped)
            continue
        if current_group:
            groups.append(current_group)
            current_group = []
    if current_group:
        groups.append(current_group)
    return groups


def _split_quote_block(block_text: str) -> QuoteBlock:
    lines: list[str] = []
    for line in block_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(">"):
            stripped = stripped[1:].strip()
        lines.append(stripped)
    if len(lines) < 2:
        raise ValidationError(f"quote block is incomplete: {block_text[:40]}")
    return QuoteBlock(original=lines[0], reading=lines[1])


def _best_effort_honka_slots(block_text: str) -> list[QuoteBlock]:
    # The new AI-source files are consumed via raw_text. These slots only remain
    # for older call sites that still expect kaji/tanden/taisho fields.
    blocks: list[QuoteBlock] = []
    quote_groups = _quote_line_groups(block_text)
    usable = min(len(quote_groups), 3)
    for index in range(usable):
        blocks.append(_split_quote_block("\n".join(quote_groups[index])))
    while len(blocks) < 3:
        blocks.append(QuoteBlock(original="", reading=""))
    return blocks


def load_honka_quotes(number: int) -> HexagramQuotes:
    text = _read_text(canonical_quotes_root() / "honka.md")
    title, block = _extract_hexagram_entry(text, number)
    quote_blocks = _best_effort_honka_slots(block)
    return HexagramQuotes(
        number=number,
        title=title,
        raw_text=block,
        kaji=quote_blocks[0],
        tanden=quote_blocks[1],
        taisho=quote_blocks[2],
    )


def build_answer_honka_block(number: int) -> str:
    return load_honka_quotes(number).raw_text


def _line_block_for_hexagram(text: str, number: int) -> str:
    _, block = _extract_hexagram_entry(text, number)
    return block


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
    raise ValidationError(f"{error_prefix} not found: {line_label}")


def _extract_line_block(block_text: str, line_label: str) -> str:
    _, section_text = _extract_line_section(
        block_text,
        line_label,
        pattern=LINE_HEADING_RE,
        error_prefix="changing line",
    )
    return section_text


def _line_heading_candidates(line_label: str) -> tuple[str, ...]:
    if line_label == "用爻":
        return ("用爻",)
    line_number = LINE_LABEL_TO_NUMBER.get(line_label)
    if line_number is not None:
        return LINE_HEADING_CANDIDATES[line_number]
    return (line_label,)


def _kanji_line_label(line_label: str) -> str:
    return KANJI_LINE_LABELS.get(line_label, line_label)


def _source_number_from_path(path: Path) -> int:
    match = TAKASHIMA_SOURCE_FILE_RE.match(path.name)
    if match is None:
        raise ValidationError(f"invalid Takashima source filename: {path}")
    return int(match.group("number"))


def _source_name_from_path(path: Path) -> str:
    match = TAKASHIMA_SOURCE_FILE_RE.match(path.name)
    if match is None:
        raise ValidationError(f"invalid Takashima source filename: {path}")
    return path.stem.split("_", 1)[1]


def _is_generic_line_title(title: str) -> bool:
    return title in GENERIC_LINE_TITLES


def load_line_heading(number: int, line_label: str) -> str:
    text = _read_text(canonical_quotes_root() / "koji.md")
    hexagram_block = _line_block_for_hexagram(text, number)
    heading, _ = _extract_line_section(
        hexagram_block,
        line_label,
        pattern=LINE_HEADING_RE,
        error_prefix="changing line",
    )
    return heading


def load_line_quotes(number: int, line_label: str) -> LineQuotes:
    text = _read_text(canonical_quotes_root() / "koji.md")
    hexagram_block = _line_block_for_hexagram(text, number)
    line_block = _extract_line_block(hexagram_block, line_label)
    quote_blocks = _collect_quote_blocks(line_block)
    if not quote_blocks:
        raise ValidationError(f"爻辞 not found: {number} {line_label}")
    return LineQuotes(
        line_label=line_label,
        raw_text=line_block,
        koji=quote_blocks[0],
        shozoden=quote_blocks[1] if len(quote_blocks) > 1 else None,
    )


def build_answer_line_block(number: int, line_label: str) -> str:
    return load_line_quotes(number, line_label).raw_text


def _extract_takashima_section(text: str, heading: str) -> str:
    match = re.search(r"^###\s+" + re.escape(heading) + r"\s*$", text, re.MULTILINE)
    if match is None:
        raise ValidationError(f"takashima section not found: {heading}")
    start = match.end()
    next_match = re.search(r"^###\s+", text[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def _extract_takashima_subsection(block_text: str, heading: str) -> str:
    for match, start, end in _heading_spans(block_text, SECTION_HEADING_RE):
        if match.group("title") == heading:
            return block_text[start:end].strip()
    raise ValidationError(f"takashima subsection not found: {heading}")


def _extract_reference_case_entry(text: str, number: int) -> tuple[str, str] | None:
    for match, start, end in _heading_spans(text, REFERENCE_CASE_HEADING_RE):
        if int(match.group("number")) == number:
            return match.group("title").strip(), text[start:end].strip()
    return None


def _extract_reference_case_sections(block_text: str, line_label: str) -> list[str]:
    expected_titles = _line_heading_candidates(line_label)
    sections: list[str] = []
    for match, start, end in _heading_spans(block_text, REFERENCE_CASE_SECTION_HEADING_RE):
        if match.group("title") not in expected_titles:
            continue
        section_text = block_text[start:end].strip()
        if section_text:
            sections.append(section_text)
    return sections


def load_reference_case_excerpt_text(number: int, line_label: str) -> str:
    text = _read_text(REFERENCE_CASES_PATH)
    entry = _extract_reference_case_entry(text, number)
    if entry is None:
        return ""
    _, block_text = entry
    sections = _extract_reference_case_sections(block_text, line_label)
    if not sections:
        return ""
    return "\n\n".join(sections).rstrip() + "\n"


def load_takashima_honka_text(path: Path) -> dict[str, str]:
    text = _strip_frontmatter(_read_text(path))
    block = _extract_takashima_section(text, "本卦解釈")
    return {
        "kaji": _extract_takashima_subsection(block, "卦辞"),
        "tanden": _extract_takashima_subsection(block, "彖伝"),
        "taisho": _extract_takashima_subsection(block, "大象伝"),
    }


def load_takashima_line_text(path: Path, line_label: str) -> str:
    text = _strip_frontmatter(_read_text(path))
    block = _extract_takashima_section(text, "変爻解釈")
    _, line_text = _extract_line_section(
        block,
        line_label,
        pattern=SECTION_HEADING_RE,
        error_prefix="takashima subsection",
    )
    return line_text


def load_takashima_line_heading(path: Path, line_label: str) -> str:
    text = _strip_frontmatter(_read_text(path))
    block = _extract_takashima_section(text, "変爻解釈")
    heading, _ = _extract_line_section(
        block,
        line_label,
        pattern=SECTION_HEADING_RE,
        error_prefix="takashima subsection",
    )
    if not _is_generic_line_title(heading):
        return heading
    return load_line_heading(_source_number_from_path(path), line_label)


def _build_honka_raw_section(label: str, path: Path, heading_suffix: str = "") -> list[str]:
    honka = load_takashima_honka_text(path)
    if label == "本卦":
        heading = _source_name_from_path(path)
    else:
        heading = f"{label}{heading_suffix}"
    return [
        f"### {heading}",
        "",
        "#### 卦辞",
        "",
        honka["kaji"],
        "",
        "#### 彖伝",
        "",
        honka["tanden"],
        "",
        "#### 大象伝",
        "",
        honka["taisho"],
        "",
    ]


def _build_line_raw_section(line_label: str, path: Path) -> list[str]:
    display_label = load_takashima_line_heading(path, line_label)
    return [
        f"### 爻辞と小象伝（{display_label}）",
        "",
        load_takashima_line_text(path, line_label),
        "",
    ]


def build_ex_simple_takashima_raw_text(path: Path, line_label: str) -> str:
    lines = ["## 高島易断", ""]
    lines.extend(_build_honka_raw_section("本卦", path))
    if line_label:
        lines.extend(_build_line_raw_section(line_label, path))
    return "\n".join(lines).rstrip() + "\n"


def build_ex_simple2_takashima_raw_text(
    main_path: Path,
    line_label: str,
    zhigua_path: Path,
    zhigua_heading_suffix: str,
) -> str:
    lines = ["## 高島易断", ""]
    lines.extend(_build_honka_raw_section("本卦", main_path))
    lines.extend(_build_line_raw_section(line_label, main_path))
    lines.extend(_build_honka_raw_section("之卦", zhigua_path, zhigua_heading_suffix))
    return "\n".join(lines).rstrip() + "\n"


def build_ex_5_takashima_raw_text(
    main_path: Path,
    main_heading_suffix: str,
    line_labels: list[str],
    zhigua_path: Path | None,
    zhigua_heading_suffix: str | None,
    auxiliary_items: list[tuple[str, Path, str]],
) -> str:
    lines = ["## 高島易断", ""]
    lines.extend(_build_honka_raw_section("本卦", main_path, main_heading_suffix))
    for line_label in line_labels:
        lines.extend(_build_line_raw_section(line_label, main_path))
    if zhigua_path is not None and zhigua_heading_suffix is not None:
        lines.extend(_build_honka_raw_section("之卦", zhigua_path, zhigua_heading_suffix))
    for label, path, heading_suffix in auxiliary_items:
        lines.extend(_build_honka_raw_section(label, path, heading_suffix))
    return "\n".join(lines).rstrip() + "\n"


def build_reference_case_excerpt_section(number: int, line_label: str) -> str:
    excerpt_text = load_reference_case_excerpt_text(number, line_label)
    if not excerpt_text:
        return ""
    return "## 占例抜粋\n\n" + excerpt_text.rstrip() + "\n"


def extract_paragraphs(text: str) -> list[str]:
    normalized = text.replace("　", "")
    parts = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    return parts


def summarize_paragraphs(text: str, limit: int | None = None) -> str:
    paragraphs = extract_paragraphs(text)
    if not paragraphs:
        return ""
    return "\n\n".join(paragraphs[:limit]).strip()


def polarity_score(texts: list[str]) -> int:
    positive = ("元吉", "大吉", "吉", "利あり", "利し", "亨る", "得る", "慶", "安んず")
    negative = ("凶", "利しからず", "利あらず", "行ってはならない", "戒", "危うい", "失う", "剝", "窮", "害")
    score = 0
    for text in texts:
        if not text:
            continue
        score += text.count("无咎") + text.count("咎なし")
        for word in positive:
            score += text.count(word)
        for word in negative:
            score -= text.count(word)
    return score


def judgment_text(score: int) -> str:
    if score >= 4:
        return "進めてよいです。"
    if score >= 1:
        return "進めてもよいですが、慎重さは必要です。"
    if score <= -4:
        return "今は進めないほうがよいです。"
    if score <= -1:
        return "今は見送る寄りで考えるのがよいです。"
    return "可否は拮抗しており、条件を見て判断すべきです。"

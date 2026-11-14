from __future__ import annotations

import re
from typing import Literal, TypedDict

from profiles import ValidationError


MODE_MARKERS = {
    "[MODE:EXTRACT]": "extract",
    "[MODE:GENERAL]": "general",
}
TEMPLATE_MARKERS = {
    "[TEMPLATE:EX_SIMPLE]": "EX_SIMPLE",
    "[TEMPLATE:EX_SIMPLE2]": "EX_SIMPLE2",
    "[TEMPLATE:EX_5]": "EX_5",
    "[TEMPLATE:EX_COMPARE]": "EX_COMPARE",
}
EXTRACT_BODY_SENTINEL = "### 3. 占い結果入力"
RANKING_HINTS = ("順番", "順位", "ランキング", "オススメ", "おすすめ")
AUXILIARY_LABELS = ("之卦", "互卦", "錯卦", "綜卦")
NON_CANDIDATE_COMPARE_HEADINGS = ("メモ", "補足", "注記", "備考")
HEXAGRAM_NUMBER_RE = re.compile(r"^(?P<number>[1-9][0-9]?)\s*(?:[\.．、]\s*|\s*)")
CHANGING_LINE_TOKEN_RE = re.compile(r"(?P<token>初爻|上爻|[1-6](?:爻)?|[二三四五]爻)")
MARKDOWN_COMPARE_HEADING_RE = re.compile(r"^#{3,6}\s+(?P<label>.+?)\s*$")
COMPARE_LABEL_PREFIX_RE = re.compile(r"^候補[^\s：:]+[：:].+")
CHANGING_LINE_NUMBER_MAP = {
    "初爻": 1,
    "1": 1,
    "1爻": 1,
    "2": 2,
    "2爻": 2,
    "二爻": 2,
    "3": 3,
    "3爻": 3,
    "三爻": 3,
    "4": 4,
    "4爻": 4,
    "四爻": 4,
    "5": 5,
    "5爻": 5,
    "五爻": 5,
    "上爻": 6,
    "6": 6,
    "6爻": 6,
}


class AuxiliaryHexagram(TypedDict):
    label: Literal["之卦", "互卦", "錯卦", "綜卦"]
    hexagram_number: int
    raw_value: str


class CompareCandidate(TypedDict):
    label: str
    hexagram_number: int
    changing_lines: list[int]


class ResolvedBase(TypedDict):
    mode: Literal["extract"]
    ranking_requested: bool


class StandardResolved(ResolvedBase):
    template: Literal["EX_SIMPLE", "EX_SIMPLE2", "EX_5"]
    main_hexagram_number: int
    changing_lines: list[int]
    auxiliary_hexagrams: list[AuxiliaryHexagram]
    hexagram_numbers: list[int]


class CompareResolved(ResolvedBase):
    template: Literal["EX_COMPARE"]
    compare_candidates: list[CompareCandidate]
    hexagram_numbers: list[int]


ResolvedInput = StandardResolved | CompareResolved


def _body_lines_after_marker(text: str) -> list[str]:
    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        if raw_line.strip() == EXTRACT_BODY_SENTINEL:
            return lines[index + 1 :]
    return lines


def _first_non_empty_line(lines: list[str]) -> tuple[int, str] | None:
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped:
            return index, stripped
    return None


def parse_mode_marker(text: str) -> str:
    lines = text.splitlines()
    first = _first_non_empty_line(lines)
    if first is None:
        raise ValidationError("MODE marker must be the first non-empty line.")
    index, marker = first
    mode = MODE_MARKERS.get(marker)
    if mode is None:
        for later in lines[index + 1 :]:
            if later.strip() in MODE_MARKERS:
                raise ValidationError("MODE marker must appear only at the top of the input.")
        allowed = ", ".join(MODE_MARKERS)
        raise ValidationError(f"MODE marker must be the first non-empty line. Use one of: {allowed}.")
    return mode


def parse_template_marker(text: str) -> str:
    lines = text.splitlines()
    first = _first_non_empty_line(lines)
    if first is None:
        raise ValidationError("MODE marker must be the first non-empty line.")
    mode_index, mode_marker = first
    if mode_marker != "[MODE:EXTRACT]":
        raise ValidationError("TEMPLATE marker is only valid for EXTRACT mode.")
    template_index = mode_index + 1
    if template_index >= len(lines):
        raise ValidationError("EXTRACT TEMPLATE marker must appear immediately after [MODE:EXTRACT].")
    template_marker = lines[template_index].strip()
    template = TEMPLATE_MARKERS.get(template_marker)
    if template is None:
        allowed = ", ".join(TEMPLATE_MARKERS)
        raise ValidationError(
            "EXTRACT TEMPLATE marker must appear immediately after [MODE:EXTRACT]. "
            f"Use one of: {allowed}."
        )
    for later in lines[template_index + 1 :]:
        if later.strip() in TEMPLATE_MARKERS:
            raise ValidationError("Multiple TEMPLATE markers found for EXTRACT input.")
    return template


def _extract_value_after_label(line: str, label: str) -> str | None:
    stripped = line.strip().lstrip("-").strip()
    prefix = f"{label}："
    if not stripped.startswith(prefix):
        return None
    return stripped[len(prefix) :].strip()


def _extract_hexagram_number(value: str) -> int | None:
    match = HEXAGRAM_NUMBER_RE.match(value.strip())
    if not match:
        return None
    number = int(match.group("number"))
    if 1 <= number <= 64:
        return number
    return None


def _extract_changing_lines(value: str) -> list[int]:
    stripped = value.strip()
    if not stripped or stripped == "なし":
        return []
    numbers: list[int] = []
    seen: set[int] = set()
    for match in CHANGING_LINE_TOKEN_RE.finditer(stripped):
        token = match.group("token")
        number = CHANGING_LINE_NUMBER_MAP[token]
        if number in seen:
            continue
        seen.add(number)
        numbers.append(number)
    if not numbers:
        raise ValidationError(
            "変爻を解釈できません。使用可能: なし、1/1爻/初爻、2/2爻/二爻、3/3爻/三爻、4/4爻/四爻、5/5爻/五爻、6/6爻/上爻。"
        )
    return numbers


def _compare_candidate_label(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    heading_match = MARKDOWN_COMPARE_HEADING_RE.match(stripped)
    if heading_match:
        label = heading_match.group("label").strip()
        if any(label == heading or label.startswith(f"{heading} ") for heading in NON_CANDIDATE_COMPARE_HEADINGS):
            return None
        return label or None
    if COMPARE_LABEL_PREFIX_RE.match(stripped):
        return stripped
    if stripped.endswith("：") and not stripped.startswith(("本卦：", "変爻：", "之卦：", "互卦：", "錯卦：", "綜卦：")):
        label = stripped[:-1].strip()
        if any(label == heading or label.startswith(heading) for heading in NON_CANDIDATE_COMPARE_HEADINGS):
            return None
        return label or None
    return None


def _iter_compare_candidate_blocks(lines: list[str]) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_label: str | None = None
    current_block: list[str] = []
    for raw_line in lines:
        candidate_label = _compare_candidate_label(raw_line)
        if candidate_label is not None:
            if current_label is not None:
                blocks.append((current_label, current_block))
            current_label = candidate_label
            current_block = []
            continue
        if current_label is not None:
            current_block.append(raw_line)
    if current_label is not None:
        blocks.append((current_label, current_block))
    return blocks


def _extract_main_hexagram(lines: list[str]) -> int:
    for raw_line in lines:
        value = _extract_value_after_label(raw_line, "本卦")
        if value is None:
            continue
        number = _extract_hexagram_number(value)
        if number is None:
            raise ValidationError("本卦の卦番号を解釈できません。")
        return number
    raise ValidationError("本卦が見つかりません。")


def _extract_main_changing_lines(lines: list[str]) -> list[int]:
    for raw_line in lines:
        value = _extract_value_after_label(raw_line, "変爻")
        if value is None:
            continue
        return _extract_changing_lines(value)
    raise ValidationError("変爻が見つかりません。")


def _extract_auxiliary_hexagrams(lines: list[str]) -> list[AuxiliaryHexagram]:
    aux: list[AuxiliaryHexagram] = []
    for label in AUXILIARY_LABELS:
        for raw_line in lines:
            value = _extract_value_after_label(raw_line, label)
            if value is None or not value or value == "なし":
                continue
            number = _extract_hexagram_number(value)
            if number is None:
                raise ValidationError(f"{label} の卦番号を解釈できません。")
            aux.append({"label": label, "hexagram_number": number, "raw_value": value})
    return aux


def extract_compare_candidates(text: str) -> list[CompareCandidate]:
    candidates: list[CompareCandidate] = []
    for label, block in _iter_compare_candidate_blocks(_body_lines_after_marker(text)):
        hexagram_number: int | None = None
        changing_lines: list[int] = []
        for raw_line in block:
            hexagram_value = _extract_value_after_label(raw_line, "本卦")
            if hexagram_value is not None:
                hexagram_number = _extract_hexagram_number(hexagram_value)
            changing_value = _extract_value_after_label(raw_line, "変爻")
            if changing_value is not None:
                changing_lines = _extract_changing_lines(changing_value)
        if hexagram_number is None:
            continue
        candidates.append(
            {
                "label": label,
                "hexagram_number": hexagram_number,
                "changing_lines": changing_lines,
            }
        )
    return candidates


def resolve_input(text: str) -> ResolvedInput:
    mode = parse_mode_marker(text)
    if mode == "general":
        raise ValidationError("[MODE:GENERAL] is recognized but not implemented in v1.")
    template = parse_template_marker(text)
    lines = _body_lines_after_marker(text)
    if template == "EX_COMPARE":
        candidates = extract_compare_candidates(text)
        if len(candidates) < 2:
            raise ValidationError("EX_COMPARE requires at least two candidates with 本卦 and 変爻.")
        payload: CompareResolved = {
            "mode": mode,
            "template": template,
            "ranking_requested": any(marker in text for marker in RANKING_HINTS),
            "compare_candidates": candidates,
            "hexagram_numbers": [candidate["hexagram_number"] for candidate in candidates],
        }
        return payload

    if template in ("EX_SIMPLE", "EX_SIMPLE2", "EX_5"):
        main_hexagram = _extract_main_hexagram(lines)
        changing_lines = _extract_main_changing_lines(lines)
        auxiliary_hexagrams = _extract_auxiliary_hexagrams(lines) if template in ("EX_SIMPLE2", "EX_5") else []
        if template == "EX_SIMPLE" and not changing_lines:
            raise ValidationError("EX_SIMPLE requires at least one changing line.")
        if template in ("EX_SIMPLE", "EX_SIMPLE2") and len(changing_lines) > 1:
            raise ValidationError(f"{template} supports at most one changing line.")
        if template == "EX_SIMPLE2":
            if not changing_lines:
                raise ValidationError("EX_SIMPLE2 requires at least one changing line.")
            zhigua = next((item for item in auxiliary_hexagrams if item["label"] == "之卦"), None)
            if zhigua is None:
                raise ValidationError("EX_SIMPLE2 requires 之卦.")
            auxiliary_hexagrams = [zhigua]
        payload: StandardResolved = {
            "mode": mode,
            "template": template,
            "ranking_requested": any(marker in text for marker in RANKING_HINTS),
            "main_hexagram_number": main_hexagram,
            "changing_lines": changing_lines,
            "auxiliary_hexagrams": auxiliary_hexagrams,
            "hexagram_numbers": [main_hexagram] + [item["hexagram_number"] for item in auxiliary_hexagrams],
        }
        return payload

    raise ValidationError(f"unsupported template: {template}")

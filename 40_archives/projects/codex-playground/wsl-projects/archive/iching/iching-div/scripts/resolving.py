from __future__ import annotations

from typing import Any
import re

from profiles import ValidationError


MODE_MARKERS = {
    "[MODE:EXTRACT]": "extract",
    "[MODE:GENERAL]": "general",
}
TEMPLATE_MARKERS = {
    "[TEMPLATE:EX_SIMPLE]": "EX_SIMPLE",
    "[TEMPLATE:EX_5]": "EX_5",
    "[TEMPLATE:EX_COMPARE]": "EX_COMPARE",
}
EXTRACT_BODY_SENTINEL = "### 3. 占い結果入力"
RANKING_HINTS = ("順番", "順位", "ランキング", "オススメ", "おすすめ")
AUXILIARY_LABELS = ("之卦", "互卦", "錯卦", "綜卦")
NON_CANDIDATE_COMPARE_HEADINGS = ("メモ", "補足", "注記", "備考")
HEXAGRAM_NUMBER_RE = re.compile(r"^(?P<number>[1-9][0-9]?)\s*(?:[\.．、]\s*|\s*)")
CHANGING_LINE_TOKEN_RE = re.compile(r"(?P<token>初爻|上爻|[1-6](?:爻)?)")


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
        if token == "初爻":
            number = 1
        elif token == "上爻":
            number = 6
        else:
            number = int(token.removesuffix("爻"))
        if number in seen:
            continue
        seen.add(number)
        numbers.append(number)
    return numbers


def _compare_candidate_label(line: str) -> str | None:
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("### "):
        label = stripped[4:].strip()
        if any(label == heading or label.startswith(f"{heading} ") for heading in NON_CANDIDATE_COMPARE_HEADINGS):
            return None
        return label or None
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


def _extract_auxiliary_hexagrams(lines: list[str]) -> list[dict[str, Any]]:
    aux: list[dict[str, Any]] = []
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


def extract_compare_candidates(text: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
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


def resolve_input(text: str) -> dict[str, Any]:
    mode = parse_mode_marker(text)
    if mode == "general":
        raise ValidationError("[MODE:GENERAL] is recognized but not implemented in split-source v1.")
    template = parse_template_marker(text)
    lines = _body_lines_after_marker(text)

    payload: dict[str, Any] = {
        "mode": mode,
        "template": template,
        "ranking_requested": any(marker in text for marker in RANKING_HINTS),
    }
    if template == "EX_COMPARE":
        candidates = extract_compare_candidates(text)
        if len(candidates) < 2:
            raise ValidationError("EX_COMPARE requires at least two candidates with 本卦 and 変爻.")
        payload["compare_candidates"] = candidates
        payload["hexagram_numbers"] = [candidate["hexagram_number"] for candidate in candidates]
    else:
        main_hexagram = _extract_main_hexagram(lines)
        changing_lines = _extract_main_changing_lines(lines)
        auxiliary_hexagrams = _extract_auxiliary_hexagrams(lines) if template == "EX_5" else []
        payload["main_hexagram_number"] = main_hexagram
        payload["changing_lines"] = changing_lines
        payload["auxiliary_hexagrams"] = auxiliary_hexagrams
        payload["hexagram_numbers"] = [main_hexagram] + [
            item["hexagram_number"] for item in auxiliary_hexagrams
        ]
    return payload

from __future__ import annotations

from typing import Any
import re

from iching_sdk.config import ValidationRuntimeError
from iching_sdk.prompting import (
    load_prompt_input,
    parse_mode_marker,
    resolve_extract_template,
)


RANKING_HINTS = (
    "順番",
    "順位",
    "ランキング",
    "オススメ",
    "おすすめ",
)

AUXILIARY_HEXAGRAM_LABELS = ("之卦", "互卦", "錯卦", "綜卦")
COMPARE_REQUIRED_LABELS = ("本卦", "変爻")
NON_CANDIDATE_COMPARE_HEADINGS = ("メモ", "補足", "注記", "備考")
HEXAGRAM_NUMBER_RE = re.compile(r"^(?P<number>[1-9][0-9]?)\s*(?:[\.．、]\s*|\s*)")
CHANGING_LINE_TOKEN_RE = re.compile(r"(?P<token>初爻|上爻|[1-6](?:爻)?)")


def _result_input_lines(text: str) -> list[str]:
    lines = text.splitlines()
    for index, raw_line in enumerate(lines):
        if raw_line.strip() == "### 3. 占い結果入力":
            return lines[index + 1 :]
    return lines


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
        candidate_label = stripped[4:].strip()
        if any(
            candidate_label == heading or candidate_label.startswith(f"{heading} ")
            for heading in NON_CANDIDATE_COMPARE_HEADINGS
        ):
            return None
        return candidate_label or None
    if stripped.endswith("：") and not any(
        stripped.startswith(f"{label}：")
        for label in (*COMPARE_REQUIRED_LABELS, *AUXILIARY_HEXAGRAM_LABELS)
    ):
        candidate_label = stripped[:-1].strip()
        if any(
            candidate_label == heading or candidate_label.startswith(heading)
            for heading in NON_CANDIDATE_COMPARE_HEADINGS
        ):
            return None
        return candidate_label or None
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


def has_extract_auxiliary_hexagrams(text: str) -> bool:
    for raw_line in _result_input_lines(text):
        for label in AUXILIARY_HEXAGRAM_LABELS:
            value = _extract_value_after_label(raw_line, label)
            if value is None:
                continue
            if value and value != "なし":
                return True
    return False


def extract_template_hexagram_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    for entry in extract_template_hexagram_entries(text):
        number = entry["hexagram_number"]
        if number not in numbers:
            numbers.append(number)
    return numbers


def extract_template_hexagram_entries(text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[int] = set()
    for raw_line in _result_input_lines(text):
        for label in ("本卦", *AUXILIARY_HEXAGRAM_LABELS):
            value = _extract_value_after_label(raw_line, label)
            if value is None or not value or value == "なし":
                continue
            number = _extract_hexagram_number(value)
            if number is None or number in seen:
                continue
            seen.add(number)
            entries.append({"label": label, "hexagram_number": number, "value": value})
    return entries


def extract_template_changing_lines(text: str) -> list[int]:
    for raw_line in _result_input_lines(text):
        value = _extract_value_after_label(raw_line, "変爻")
        if value is None:
            continue
        return _extract_changing_lines(value)
    return []


def extract_compare_hexagram_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    seen: set[int] = set()
    for _, candidate_block in _iter_compare_candidate_blocks(_result_input_lines(text)):
        for raw_line in candidate_block:
            value = _extract_value_after_label(raw_line, "本卦")
            if value is None:
                continue
            number = _extract_hexagram_number(value)
            if number is None or number in seen:
                continue
            seen.add(number)
            numbers.append(number)
    return numbers


def count_compare_candidates(text: str) -> int:
    lines = _result_input_lines(text)
    count = 0
    for _, candidate_block in _iter_compare_candidate_blocks(lines):
        block_lines = [line.strip().lstrip("-").strip() for line in candidate_block if line.strip()]
        has_hexagram = any(line.startswith("本卦：") for line in block_lines)
        has_changing_line = any(line.startswith("変爻：") for line in block_lines)
        if has_hexagram and has_changing_line:
            count += 1
    return count


def extract_compare_candidates(text: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for label, candidate_block in _iter_compare_candidate_blocks(_result_input_lines(text)):
        hexagram_number: int | None = None
        changing_lines: list[int] = []
        for raw_line in candidate_block:
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


def detect_input_kind(mode: str, text: str) -> str:
    template_name = resolve_extract_template(text)
    if template_name == "EX_COMPARE":
        return "extract_comparison"
    return "extract_template"


def build_source_groups(mode: str) -> list[str]:
    return ["extract_takashima"]


def build_hints(mode: str, text: str, input_kind: str) -> list[str]:
    hints: list[str] = []
    if mode == "extract":
        template_name = resolve_extract_template(text)
        hints.append("requires_strict_citation")
        hints.append("template_marker_present")
        if template_name == "EX_5" and has_extract_auxiliary_hexagrams(text):
            hints.append("auxiliary_hexagrams_present")
    if input_kind == "extract_comparison":
        hints.append("comparison_requested")
        if any(marker in text for marker in RANKING_HINTS):
            hints.append("ranking_requested")
    return hints


def resolve_loaded_input(
    input_source: str,
    input_text: str,
    override_mode: str | None,
) -> dict[str, Any]:
    input_mode = parse_mode_marker(input_text)
    mode = override_mode or input_mode
    input_kind = detect_input_kind(mode, input_text)
    payload: dict[str, Any] = {
        "mode": mode,
        "input_source": input_source,
        "input_kind": input_kind,
        "source_groups": build_source_groups(mode),
        "hints": build_hints(mode, input_text, input_kind),
    }
    template_name = resolve_extract_template(input_text)
    payload["template"] = template_name
    hexagram_numbers = (
        extract_compare_hexagram_numbers(input_text)
        if template_name == "EX_COMPARE"
        else extract_template_hexagram_numbers(input_text)
    )
    if hexagram_numbers:
        payload["hexagram_numbers"] = hexagram_numbers
    if template_name == "EX_5":
        hexagram_entries = extract_template_hexagram_entries(input_text)
        if hexagram_entries:
            payload["hexagram_entries"] = hexagram_entries
            payload["auxiliary_hexagrams"] = [
                entry for entry in hexagram_entries if entry.get("label") != "本卦"
            ]
    changing_lines = extract_template_changing_lines(input_text)
    if changing_lines:
        payload["changing_lines"] = changing_lines
    if template_name == "EX_COMPARE":
        candidates = extract_compare_candidates(input_text)
        candidate_count = len(candidates)
        payload["compare_candidate_count"] = candidate_count
        payload["compare_candidates"] = candidates
        if candidate_count < 2:
            raise ValidationRuntimeError(
                "EX_COMPARE requires at least two candidates in the result input block."
            )
    if template_name == "EX_5":
        payload["has_auxiliary_hexagrams"] = has_extract_auxiliary_hexagrams(input_text)
    return payload


def resolve_input_text(
    input_arg: str,
    override_mode: str | None,
) -> dict[str, Any]:
    input_source, input_text = load_prompt_input(input_arg)
    return resolve_loaded_input(input_source, input_text, override_mode)

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from indexing import load_takashima_catalog
from profiles import ValidationError, takashima_provider
from rendering import build_answer_honka_block, build_answer_line_block, load_takashima_line_heading
from resolving import ResolvedInput, resolve_input
from selecting import SelectionResult, select_sources
from workflow import QUESTION_HEADING, RAW_APPENDIX_HEADING, REFERENCES_HEADING, line_labels_from_numbers, line_label_from_numbers, validate_answer_shape


TOTAL_INTERPRETATION_HEADING = "## 総合解釈"
SECTION_REFERENCE_RE = re.compile(r"^（参照：.+）$")


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"input file not found: {path}")
    return path.read_text(encoding="utf-8")


def _read_answer_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"answer file not found: {path}")
    return path.read_text(encoding="utf-8")


def _normalize_heading(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("## "):
        return stripped[3:].strip()
    if stripped.startswith("**") and stripped.endswith("**") and len(stripped) >= 4:
        return stripped[2:-2].strip()
    return None


def _heading_parts(label: str) -> tuple[str, str | None]:
    match = re.match(r"^(本卦|変爻|之卦|互卦|錯卦|綜卦)(?:（(.+)）)?$", label)
    if not match:
        return label, None
    return match.group(1), match.group(2)


def _extract_hexagram_number(text: str | None) -> int | None:
    if not text:
        return None
    match = re.match(r"^(\d+)\s+", text)
    if not match:
        return None
    return int(match.group(1))


def _heading_variants(expected_label: str, resolved: ResolvedInput | None = None) -> tuple[str, ...]:
    expected = expected_label
    if expected.startswith("## "):
        expected = expected[3:].strip()
    elif expected.startswith("**") and expected.endswith("**") and len(expected) >= 4:
        expected = expected[2:-2].strip()
    variants = [expected]
    if resolved is None or resolved["template"] == "EX_COMPARE":
        return tuple(variants)
    provider = takashima_provider()
    catalog = load_takashima_catalog(provider)
    if expected == "本卦":
        variants.append(catalog[resolved["main_hexagram_number"]].name)
    elif expected == "変爻":
        main_source = catalog[resolved["main_hexagram_number"]]
        for line_label in line_labels_from_numbers(resolved["changing_lines"]):
            variants.append(load_takashima_line_heading(main_source.file_path, line_label))
    else:
        for item in resolved.get("auxiliary_hexagrams", []):
            if expected == item["label"]:
                variants.append(f"{item['label']}：{catalog[item['hexagram_number']].name}")
                break
    return tuple(variants)


def _heading_matches(actual_line: str, expected_label: str, resolved: ResolvedInput | None = None) -> bool:
    actual = _normalize_heading(actual_line)
    if actual is None:
        return False
    for expected in _heading_variants(expected_label, resolved):
        if actual == expected:
            return True
        actual_role, actual_body = _heading_parts(actual)
        expected_role, expected_body = _heading_parts(expected)
        if actual_role != expected_role:
            continue
        if expected_body is None:
            return True
        actual_number = _extract_hexagram_number(actual_body)
        expected_number = _extract_hexagram_number(expected_body)
        if actual_number is not None and expected_number is not None and actual_number == expected_number:
            return True
        if actual_body == expected_body:
            return True
    return False


def _find_heading_index(lines: list[str], label: str, resolved: ResolvedInput | None = None) -> int:
    for index, line in enumerate(lines):
        if _heading_matches(line, label, resolved):
            return index
    raise ValidationError(f"section heading not found in answer: {label}")


def _find_heading_index_from(lines: list[str], label: str, start_index: int, resolved: ResolvedInput | None = None) -> int:
    for index in range(start_index, len(lines)):
        if _heading_matches(lines[index], label, resolved):
            return index
    raise ValidationError(f"section heading not found in answer: {label}")


def _find_interpretation_index(lines: list[str], heading_index: int, heading_label: str) -> int:
    interpretation_heading = f"### {heading_label}解釈"
    for index in range(heading_index + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped == interpretation_heading:
            return index
        if index > heading_index + 1 and _normalize_heading(lines[index]) is not None:
            break
        if stripped in {TOTAL_INTERPRETATION_HEADING, REFERENCES_HEADING, RAW_APPENDIX_HEADING}:
            break
    label = _normalize_heading(lines[heading_index]) or lines[heading_index].strip()
    raise ValidationError(f"interpretation heading not found after: {label}")


def _find_section_end_index(lines: list[str], heading_index: int) -> int:
    for index in range(heading_index + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped in {TOTAL_INTERPRETATION_HEADING, REFERENCES_HEADING, RAW_APPENDIX_HEADING}:
            return index
        if index > heading_index + 1 and _normalize_heading(lines[index]) is not None:
            return index
    return len(lines)


def _normalize_section_heading(lines: list[str], heading_label: str) -> list[str]:
    heading_index = _find_heading_index(lines, heading_label)
    lines = list(lines)
    lines[heading_index] = f"## {heading_label}"
    return lines


def _replace_section_block(
    lines: list[str],
    heading_label: str,
    block_text: str,
    *,
    start_index: int = 0,
    resolved: ResolvedInput | None = None,
) -> tuple[list[str], int]:
    heading_index = _find_heading_index_from(lines, heading_label, start_index, resolved)
    lines = list(lines)
    lines[heading_index] = f"## {heading_label}"
    replacement = ["", *block_text.splitlines(), ""]
    if heading_label in {"本卦", "変爻"}:
        section_end = _find_section_end_index(lines, heading_index)
        updated = lines[: heading_index + 1] + replacement + lines[section_end:]
        next_index = heading_index + 1 + len(replacement)
        return updated, next_index
    try:
        interpretation_index = _find_interpretation_index(lines, heading_index, heading_label)
    except ValidationError:
        section_end = _find_section_end_index(lines, heading_index)
        updated = lines[: heading_index + 1] + replacement + lines[section_end:]
        next_index = heading_index + 1 + len(replacement)
        return updated, next_index
    updated = lines[: heading_index + 1] + replacement + lines[interpretation_index:]
    next_index = heading_index + 1 + len(replacement)
    return updated, next_index


def _apply_display_headings(lines: list[str], resolved: ResolvedInput) -> list[str]:
    if resolved["template"] == "EX_COMPARE":
        return lines
    provider = takashima_provider()
    catalog = load_takashima_catalog(provider)
    main_source = catalog[resolved["main_hexagram_number"]]
    updated = list(lines)
    heading_index = _find_heading_index(updated, "本卦", resolved)
    updated[heading_index] = f"## {main_source.name}"
    search_offset = heading_index + 1
    for line_label in line_labels_from_numbers(resolved["changing_lines"]):
        heading_index = _find_heading_index_from(updated, "変爻", search_offset, resolved)
        updated[heading_index] = f"## {load_takashima_line_heading(main_source.file_path, line_label)}"
        search_offset = heading_index + 1
    for item in resolved.get("auxiliary_hexagrams", []):
        heading_index = _find_heading_index(updated, item["label"], resolved)
        updated[heading_index] = f"## {item['label']}：{catalog[item['hexagram_number']].name}"
    return updated


def _build_section_blocks(resolved: ResolvedInput) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = [("本卦", build_answer_honka_block(resolved["main_hexagram_number"]))]

    line_labels = line_labels_from_numbers(resolved["changing_lines"])
    if resolved["template"] in ("EX_SIMPLE", "EX_SIMPLE2") and line_labels:
        blocks.append(("変爻", build_answer_line_block(resolved["main_hexagram_number"], line_labels[0])))

    if resolved["template"] in ("EX_SIMPLE2", "EX_5"):
        if line_labels:
            if resolved["template"] == "EX_5":
                for line_label in line_labels:
                    blocks.append(("変爻", build_answer_line_block(resolved["main_hexagram_number"], line_label)))
        for item in resolved.get("auxiliary_hexagrams", []):
            blocks.append((item["label"], build_answer_honka_block(item["hexagram_number"])))
    return blocks


def _remove_section_reference_lines(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        if SECTION_REFERENCE_RE.match(line.strip()):
            if cleaned and cleaned[-1] == "":
                cleaned.pop()
            continue
        cleaned.append(line)
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return cleaned


def _remove_references_section(lines: list[str]) -> list[str]:
    cleaned: list[str] = []
    index = 0
    while index < len(lines):
        if _heading_matches(lines[index], REFERENCES_HEADING):
            index += 1
            while index < len(lines):
                if _heading_matches(lines[index], RAW_APPENDIX_HEADING) or _normalize_heading(lines[index]) is not None:
                    break
                index += 1
            while cleaned and cleaned[-1] == "":
                cleaned.pop()
            continue
        cleaned.append(lines[index])
        index += 1
    while cleaned and cleaned[-1] == "":
        cleaned.pop()
    return cleaned


def _build_question_block(input_text: str) -> str:
    return "\n".join(["```text", input_text.rstrip(), "```"])


def _build_reference_section(selection: SelectionResult) -> list[str]:
    reference_lines = [REFERENCES_HEADING]
    seen: set[str] = set()
    for item in selection["selected_items"]:
        citation_file = item["citation_file"]
        if citation_file in seen:
            continue
        seen.add(citation_file)
        reference_lines.append(f"- {citation_file} | {item['hexagram_name']}")
    return reference_lines


def assemble_answer(input_path: Path, answer_path: Path) -> str:
    input_text = _read_text(input_path)
    resolved: ResolvedInput = resolve_input(input_text)
    answer_text = _read_answer_text(answer_path)
    validate_answer_shape(resolved, answer_text, stage="draft")
    lines = answer_text.splitlines()
    lines = _remove_section_reference_lines(lines)
    lines = _remove_references_section(lines)
    search_offsets: dict[str, int] = {}
    question_block = _build_question_block(input_text)
    lines, next_index = _replace_section_block(
        lines,
        QUESTION_HEADING.removeprefix("## "),
        question_block,
        start_index=0,
        resolved=resolved,
    )
    search_offsets[QUESTION_HEADING.removeprefix("## ")] = next_index
    if resolved["template"] == "EX_COMPARE":
        assembled = "\n".join(lines).rstrip() + "\n"
        validate_answer_shape(resolved, assembled, stage="assembled")
        return assembled
    selection: SelectionResult = select_sources(takashima_provider(), resolved)
    for heading_label, block_text in _build_section_blocks(resolved):
        lines, next_index = _replace_section_block(
            lines,
            heading_label,
            block_text,
            start_index=search_offsets.get(heading_label, 0),
            resolved=resolved,
        )
        search_offsets[heading_label] = next_index
    while lines and lines[-1] == "":
        lines.pop()
    lines.extend(["", *_build_reference_section(selection)])
    lines = _apply_display_headings(lines, resolved)
    assembled = "\n".join(lines).rstrip() + "\n"
    validate_answer_shape(resolved, assembled, stage="assembled")
    return assembled


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inject classical quote blocks into an answer file.")
    parser.add_argument("--input", required=True, help="Input file path.")
    parser.add_argument("--output", required=True, help="Output answer path to rewrite in place.")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)
    try:
        output_path.write_text(assemble_answer(input_path, output_path), encoding="utf-8")
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

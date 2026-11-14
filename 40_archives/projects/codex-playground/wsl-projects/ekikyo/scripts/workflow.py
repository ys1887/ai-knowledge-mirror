from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from indexing import load_takashima_catalog
from profiles import ValidationError, takashima_provider
from rendering import load_takashima_line_heading
from resolving import ResolvedInput


WORK_FILENAME_RE = re.compile(r"^(?P<day>\d{4}-\d{2}-\d{2})_(?P<number>\d{2})\.md$")
QUESTION_HEADING = "## 質問文"
REFERENCES_HEADING = "## 参照"
RAW_APPENDIX_HEADING = "## 高島易断"
SECTION_HEADING_RE = re.compile(r"^(本卦|変爻|之卦|互卦|錯卦|綜卦)(?:（.+）)?$")


@dataclass(frozen=True)
class RequiredSection:
    heading: str
    fixed_text: str | None = None


def line_labels_from_numbers(line_numbers: list[int]) -> list[str]:
    labels: list[str] = []
    for line in line_numbers:
        if line == 1:
            labels.append("初爻")
        elif line == 6:
            labels.append("上爻")
        else:
            labels.append(f"{line}爻")
    return labels


def line_label_from_numbers(line_numbers: list[int]) -> str:
    labels = line_labels_from_numbers(line_numbers)
    if not labels:
        return ""
    if len(labels) != 1:
        raise ValidationError("workflow helpers currently support a single changing line")
    return labels[0]


def _display_heading_candidates(resolved: ResolvedInput, expected_heading: str) -> tuple[str, ...]:
    expected = expected_heading.removeprefix("## ").strip()
    if resolved["template"] == "EX_COMPARE":
        return (expected,)
    provider = takashima_provider()
    catalog = load_takashima_catalog(provider)
    if expected == "本卦":
        return (expected, catalog[resolved["main_hexagram_number"]].name)
    if expected == "変爻":
        main_source = catalog[resolved["main_hexagram_number"]]
        labels = [expected]
        for line_label in line_labels_from_numbers(resolved["changing_lines"]):
            labels.append(load_takashima_line_heading(main_source.file_path, line_label))
        return tuple(labels)
    for item in resolved.get("auxiliary_hexagrams", []):
        if expected == item["label"]:
            source = catalog[item["hexagram_number"]]
            return (expected, f"{item['label']}：{source.name}")
    return (expected,)


def next_work_output_path(work_dir: Path, *, today: date | None = None) -> Path:
    current_day = today or date.today()
    prefix = current_day.isoformat()
    next_number = 1
    if work_dir.exists():
        if not work_dir.is_dir():
            raise ValidationError(f"work directory not found or not a directory: {work_dir}")
        for child in work_dir.iterdir():
            match = WORK_FILENAME_RE.match(child.name)
            if match is None or match.group("day") != prefix:
                continue
            next_number = max(next_number, int(match.group("number")) + 1)
    return work_dir / f"{prefix}_{next_number:02d}.md"


def _required_sections(resolved: ResolvedInput) -> list[RequiredSection]:
    template = resolved["template"]
    sections = [RequiredSection(QUESTION_HEADING), RequiredSection("## 本卦")]

    if template == "EX_COMPARE":
        return sections

    if template == "EX_SIMPLE":
        sections.append(RequiredSection("## 変爻"))
        return sections

    if template == "EX_SIMPLE2":
        sections.append(RequiredSection("## 変爻"))
        sections.append(RequiredSection("## 之卦"))
        return sections

    if resolved["changing_lines"]:
        for _ in resolved["changing_lines"]:
            sections.append(RequiredSection("## 変爻"))
    for item in resolved.get("auxiliary_hexagrams", []):
        sections.append(RequiredSection(f"## {item['label']}"))
    return sections


def build_answer_skeleton(resolved: ResolvedInput) -> str:
    if resolved["template"] == "EX_COMPARE":
        provider = takashima_provider()
        catalog = load_takashima_catalog(provider)
        lines = [QUESTION_HEADING, "", "**核心・結論**", "", "**吉凶順位（1位 = 最吉）**", ""]
        for index, candidate in enumerate(resolved["compare_candidates"], start=1):
            lines.append(f"{index}. ")
        lines.append("")
        for index, candidate in enumerate(resolved["compare_candidates"], start=1):
            source = catalog[candidate["hexagram_number"]]
            line_label = line_label_from_numbers(candidate["changing_lines"])
            lines.extend(
                [
                    f"### {index}位 {candidate['label']}（{source.name}・{line_label}）",
                    "",
                    "（引用ブロックをここに記述）",
                    "",
                    "（解釈段落をここに記述）",
                    "",
                    f"（参照：takashima/{source.file_path.name}|{source.name}）",
                    "",
                ]
            )
        lines.extend(
            [
                "**まとめ**",
                "",
                "| 順位 | 候補 | 根拠 |",
                "| --- | --- | --- |",
            ]
        )
        for index, candidate in enumerate(resolved["compare_candidates"], start=1):
            lines.append(f"| {index}位 | {candidate['label']} |  |")
        lines.extend(["", f"今回のおすすめは、{resolved['compare_candidates'][0]['label']}です。"])
        return "\n".join(lines).rstrip() + "\n"

    lines: list[str] = []
    for section in _required_sections(resolved):
        lines.append(section.heading)
        lines.append("")
        if section.fixed_text:
            lines.append(section.fixed_text)
            lines.append("")
    lines.extend([REFERENCES_HEADING, ""])
    return "\n".join(lines).rstrip() + "\n"


def _normalize_heading(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("## "):
        return stripped[3:].strip()
    if stripped.startswith("**") and stripped.endswith("**") and len(stripped) >= 4:
        return stripped[2:-2].strip()
    return None


def _matches_heading(actual_line: str, expected_heading: str, resolved: ResolvedInput | None = None) -> bool:
    actual = _normalize_heading(actual_line)
    if actual is None:
        return False
    expected_variants = (expected_heading.removeprefix("## ").strip(),)
    if resolved is not None:
        expected_variants = _display_heading_candidates(resolved, expected_heading)
    for expected in expected_variants:
        if actual == expected:
            return True
        actual_match = SECTION_HEADING_RE.match(actual)
        expected_match = SECTION_HEADING_RE.match(expected)
        if actual_match is None or expected_match is None:
            continue
        if actual_match.group(1) == expected_match.group(1):
            return True
    return False


def _count_heading(lines: list[str], heading: str, resolved: ResolvedInput | None = None) -> int:
    if heading.startswith("## "):
        return sum(1 for line in lines if _matches_heading(line, heading, resolved))
    return sum(1 for line in lines if line.strip() == heading)


def _ensure_present(lines: list[str], heading: str, *, message: str, resolved: ResolvedInput | None = None) -> None:
    if _count_heading(lines, heading, resolved) < 1:
        raise ValidationError(message)


def find_heading_index(lines: list[str], heading: str, resolved: ResolvedInput | None = None) -> int:
    for index, line in enumerate(lines):
        if heading.startswith("## "):
            if _matches_heading(line, heading, resolved):
                return index
            continue
        if line.strip() == heading:
            return index
    raise ValidationError(f"required section heading not found: {heading}")


def validate_answer_shape(resolved: ResolvedInput, text: str, *, stage: str) -> None:
    lines = text.splitlines()
    template = resolved["template"]

    if not lines or lines[0].strip() != QUESTION_HEADING:
        raise ValidationError(f"required section heading not found: {QUESTION_HEADING}")
    if _count_heading(lines, QUESTION_HEADING, resolved) != 1:
        raise ValidationError(f"required section heading not found: {QUESTION_HEADING}")

    if template == "EX_COMPARE":
        _ensure_present(lines, "**核心・結論**", message="required section heading not found: **核心・結論**", resolved=resolved)
        _ensure_present(
            lines,
            "**吉凶順位（1位 = 最吉）**",
            message="required section heading not found: **吉凶順位（1位 = 最吉）**",
            resolved=resolved,
        )
        _ensure_present(lines, "**まとめ**", message="required section heading not found: **まとめ**", resolved=resolved)
        return

    for section in _required_sections(resolved):
        _ensure_present(lines, section.heading, message=f"required section heading not found: {section.heading}", resolved=resolved)

    if template == "EX_5":
        expected_line_sections = len(resolved["changing_lines"])
        actual_line_sections = _count_heading(lines, "## 変爻", resolved)
        if actual_line_sections != expected_line_sections:
            raise ValidationError(f"EX_5 requires {expected_line_sections} 変爻 sections, found {actual_line_sections}")

    if stage in ("assembled", "final"):
        _ensure_present(lines, REFERENCES_HEADING, message=f"required section heading not found: {REFERENCES_HEADING}", resolved=resolved)
        if _count_heading(lines, REFERENCES_HEADING, resolved) != 1:
            raise ValidationError("references section must appear exactly once")

    if stage == "final" and template in ("EX_SIMPLE", "EX_SIMPLE2", "EX_5"):
        _ensure_present(lines, RAW_APPENDIX_HEADING, message=f"required section heading not found: {RAW_APPENDIX_HEADING}", resolved=resolved)
        if find_heading_index(lines, REFERENCES_HEADING, resolved) > find_heading_index(lines, RAW_APPENDIX_HEADING, resolved):
            raise ValidationError("references section must appear before raw appendix")

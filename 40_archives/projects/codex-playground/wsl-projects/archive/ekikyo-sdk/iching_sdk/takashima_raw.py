from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from iching_sdk.config import ValidationRuntimeError
from iching_sdk.profiles import load_split_catalog


FRONTMATTER_RE = re.compile(r"^---\s*$", re.MULTILINE)
MARKER_RE = re.compile(r"^\*\*(?P<marker>読み下し|解釈)\*\*$", re.MULTILINE)


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationRuntimeError(f"Takashima raw appendix source file not found: {path}")
    return path.read_text(encoding="utf-8")


def _strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[index + 1 :]).lstrip("\n")
    return text


def _extract_after_marker(text: str, marker: str) -> str:
    match = re.search(rf"^\*\*{re.escape(marker)}\*\*$", text, re.MULTILINE)
    if match is None:
        raise ValidationRuntimeError(f"Takashima raw appendix marker not found: {marker}")
    start = match.end()
    next_match = MARKER_RE.search(text, start)
    end = next_match.start() if next_match else len(text)
    return text[start:end].strip()


def _extract_main_prose(path: Path) -> str:
    text = _strip_frontmatter(_read_text(path))
    return _extract_after_marker(text, "読み下し")


def _extract_line_prose(path: Path) -> str:
    text = _strip_frontmatter(_read_text(path))
    return _extract_after_marker(text, "解釈")


def _line_label_from_section_name(section_name: str) -> str | None:
    if section_name.startswith("yao_"):
        try:
            line_number = int(section_name.removeprefix("yao_"))
        except ValueError:
            return None
        if line_number == 1:
            return "初爻"
        if line_number == 6:
            return "上爻"
        return f"{line_number}爻"
    if section_name == "yongjiu":
        return "用九"
    if section_name == "yongliu":
        return "用六"
    return None


def _append_block(lines: list[str], heading: str, body_lines: list[str]) -> None:
    lines.append(heading)
    lines.append("")
    lines.extend(body_lines)
    lines.append("")


def _build_hexagram_block(
    label: str,
    number: int,
    name: str,
    section_root: Path,
    section_files: list[str],
    section_names: list[str],
) -> list[str]:
    lines: list[str] = [f"### {label}（{number} {name}）", ""]
    section_lookup = {
        section_name: section_root / section_file
        for section_name, section_file in zip(section_names, section_files, strict=False)
    }
    for section_name, heading in (("kaji", "卦辞"), ("tanden", "彖伝"), ("taisho", "大象伝")):
        section_path = section_lookup.get(section_name)
        if section_path is None:
            continue
        _append_block(lines, f"#### {heading}", [_extract_main_prose(section_path)])
    return lines


def _build_line_block(label: str, line_path: Path) -> list[str]:
    return [f"### 変爻（{label}）", "", _extract_line_prose(line_path), ""]


def build_takashima_raw_appendix(
    answer_text: str,
    resolved: dict[str, Any],
    selection: dict[str, Any] | None,
) -> str:
    if not selection or resolved.get("mode") != "extract":
        return answer_text
    template_name = resolved.get("template")
    if template_name not in {"EX_SIMPLE", "EX_5"}:
        return answer_text
    if "## 高島解釈原文" in answer_text:
        return answer_text

    section_root_value = selection.get("selected_section_root")
    selected_sections = selection.get("selected_sections", [])
    if not isinstance(section_root_value, str) or not selected_sections:
        return answer_text

    section_root = Path(section_root_value)
    catalog = load_split_catalog(section_root)
    auxiliary_hexagrams = resolved.get("auxiliary_hexagrams", [])
    appendix_lines: list[str] = ["## 高島解釈原文", ""]

    for index, selected_section in enumerate(selected_sections):
        hexagram_number = selected_section.get("hexagram_number")
        if not isinstance(hexagram_number, int):
            continue
        source = catalog.get(hexagram_number)
        if source is None:
            raise ValidationRuntimeError(
                f"Takashima raw appendix source is not indexed: {hexagram_number}"
            )

        if index == 0:
            label = "本卦"
        else:
            aux_index = index - 1
            aux_label = None
            if isinstance(auxiliary_hexagrams, list) and aux_index < len(auxiliary_hexagrams):
                candidate = auxiliary_hexagrams[aux_index]
                if isinstance(candidate, dict):
                    raw_label = candidate.get("label")
                    if isinstance(raw_label, str) and raw_label:
                        aux_label = raw_label
            label = aux_label or "補助卦"

        section_files = selected_section.get("section_files", [])
        section_names = selected_section.get("sections", [])
        if not isinstance(section_files, list) or not isinstance(section_names, list):
            continue

        appendix_lines.extend(
            _build_hexagram_block(
                label,
                source.number,
                source.name,
                section_root,
                section_files,
                section_names,
            )
        )

        if index != 0:
            continue

        section_lookup = {
            section_name: section_root / section_file
            for section_name, section_file in zip(section_names, section_files, strict=False)
        }
        for section_name in section_names:
            line_label = _line_label_from_section_name(section_name)
            if line_label is None:
                continue
            line_path = section_lookup.get(section_name)
            if line_path is None:
                continue
            appendix_lines.extend(_build_line_block(line_label, line_path))

    while appendix_lines and appendix_lines[-1] == "":
        appendix_lines.pop()
    appendix_text = "\n".join(appendix_lines).rstrip() + "\n"
    base_text = answer_text.rstrip("\n")
    if not base_text:
        return appendix_text
    return base_text + "\n\n" + appendix_text

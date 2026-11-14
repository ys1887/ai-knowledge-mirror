from __future__ import annotations

import re
from typing import Any

from iching_sdk.config import ExtractProfileConfig, ValidationRuntimeError, repo_root
from iching_sdk.validation import read_input_text


MODE_MARKERS = {
    "extract": "[MODE:EXTRACT]",
    "general": "[MODE:GENERAL]",
}
EXTRACT_TEMPLATES = {
    "EX_SIMPLE": {
        "marker": "[TEMPLATE:EX_SIMPLE]",
        "fragment": "extract_simple.md",
        "split_fragment": "extract_simple_split.md",
        "input_kind": "extract_template",
    },
    "EX_5": {
        "marker": "[TEMPLATE:EX_5]",
        "fragment": "extract_5.md",
        "split_fragment": "extract_5_split.md",
        "input_kind": "extract_template",
    },
    "EX_COMPARE": {
        "marker": "[TEMPLATE:EX_COMPARE]",
        "fragment": "extract_compare.md",
        "split_fragment": "extract_compare_split.md",
        "input_kind": "extract_comparison",
    },
}
MODE_MARKER_RE = re.compile(r"^\[MODE:(?P<value>[^\]]+)\]$")
TEMPLATE_MARKER_RE = re.compile(r"^\[TEMPLATE:(?P<value>[^\]]+)\]$")

ALLOWED_MODE_MARKERS_TEXT = ", ".join(MODE_MARKERS[mode] for mode in ("extract", "general"))
ALLOWED_EXTRACT_TEMPLATE_MARKERS_TEXT = ", ".join(
    template["marker"] for template in EXTRACT_TEMPLATES.values()
)


def load_prompt_fragment(name: str) -> str:
    prompt_path = repo_root() / "prompts" / "fragments" / name
    if not prompt_path.is_file():
        raise ValidationRuntimeError(f"prompt fragment not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8").strip()


def resolve_extract_template_fragment(
    template_name: str,
    profile: ExtractProfileConfig | None,
) -> str:
    template = EXTRACT_TEMPLATES[template_name]
    if profile is not None and profile.extract_source_kind == "split":
        split_fragment = template.get("split_fragment")
        if isinstance(split_fragment, str):
            return split_fragment
    return template["fragment"]


def body_lines_after(index: int, lines: list[str]) -> list[str]:
    return [line.strip() for line in lines[index + 1 :] if line.strip()]


def find_first_non_empty_line(lines: list[str]) -> tuple[int, str] | None:
    for index, raw_line in enumerate(lines):
        stripped = raw_line.strip()
        if stripped:
            return index, stripped
    return None


def parse_mode_marker(text: str) -> str:
    lines = text.splitlines()
    first_non_empty = find_first_non_empty_line(lines)
    if first_non_empty is None:
        raise ValidationRuntimeError(
            "MODE marker must be the first non-empty line. "
            f"Use {ALLOWED_MODE_MARKERS_TEXT}."
        )

    mode_index, mode_line = first_non_empty
    marker_lookup = {marker: mode for mode, marker in MODE_MARKERS.items()}
    match = MODE_MARKER_RE.fullmatch(mode_line)
    if match and mode_line not in marker_lookup:
        raise ValidationRuntimeError(
            f"Unknown MODE marker. Allowed values: {ALLOWED_MODE_MARKERS_TEXT}."
        )
    if mode_line in marker_lookup:
        return marker_lookup[mode_line]

    for later_line in body_lines_after(mode_index, lines):
        if MODE_MARKER_RE.fullmatch(later_line):
            raise ValidationRuntimeError(
                "MODE marker must appear only at the top of the input before the body starts."
            )
    raise ValidationRuntimeError(
        "MODE marker must be the first non-empty line. "
        f"Use {ALLOWED_MODE_MARKERS_TEXT}."
    )


def parse_extract_template_marker(text: str) -> str:
    lines = text.splitlines()
    first_non_empty = find_first_non_empty_line(lines)
    if first_non_empty is None:
        raise ValidationRuntimeError(
            "MODE marker must be the first non-empty line. "
            f"Use {ALLOWED_MODE_MARKERS_TEXT}."
        )
    mode_index, _ = first_non_empty
    marker_lookup = {
        template["marker"]: template_name for template_name, template in EXTRACT_TEMPLATES.items()
    }
    next_index = mode_index + 1
    if next_index >= len(lines):
        raise ValidationRuntimeError(
            "EXTRACT TEMPLATE marker must appear immediately after [MODE:EXTRACT]."
        )
    next_line = lines[next_index].strip()
    match = TEMPLATE_MARKER_RE.fullmatch(next_line)
    later_template_markers = [
        later_line
        for later_line in body_lines_after(next_index, lines)
        if TEMPLATE_MARKER_RE.fullmatch(later_line)
    ]
    if next_line in marker_lookup:
        if later_template_markers:
            raise ValidationRuntimeError(
                "Multiple TEMPLATE markers found for EXTRACT. "
                f"Use exactly one of: {ALLOWED_EXTRACT_TEMPLATE_MARKERS_TEXT}."
            )
        return marker_lookup[next_line]
    if match:
        raise ValidationRuntimeError(
            "Unknown TEMPLATE marker for EXTRACT. "
            f"Allowed values: {ALLOWED_EXTRACT_TEMPLATE_MARKERS_TEXT}."
        )
    if later_template_markers:
        raise ValidationRuntimeError(
            "TEMPLATE marker must appear only in the EXTRACT header block before the body starts."
        )
    raise ValidationRuntimeError(
        "EXTRACT TEMPLATE marker must appear immediately after [MODE:EXTRACT]."
    )


def detect_mode(text: str) -> str:
    return parse_mode_marker(text)


def resolve_prompt_mode(input_text: str, override_mode: str | None) -> str:
    input_mode = detect_mode(input_text)
    if override_mode:
        return override_mode
    return input_mode


def resolve_extract_template(input_text: str) -> str:
    return parse_extract_template_marker(input_text)


def format_selected_sources(selection: dict[str, Any] | None) -> list[str]:
    if not selection:
        return []
    sections = ["## Selected Sources"]
    for group in selection.get("selected_groups", []):
        sections.append(f"- {group['group']}:")
        files = group.get("files", [])
        if not files:
            sections.append("  (none)")
            continue
        sections.extend([f"  - {path}" for path in files])
    selected_count = selection.get("selected_file_count")
    if selected_count is not None:
        sections.extend(["", f"Selected file count: {selected_count}"])
    return sections


def format_citation_filenames(mode: str, selection: dict[str, Any] | None) -> list[str]:
    if mode != "extract" or not selection:
        return []
    selected_files = selection.get("selected_files", [])
    if not selected_files:
        return []
    sections = [
        "## Citation Filenames",
        "- 参照行では次の相対パスをそのまま使うこと。",
        "- `34_雷天大壮.md` のような basename だけの表記は禁止。",
    ]
    sections.extend([f"- `{path}`" for path in selected_files])
    return sections


def format_selected_section_sources(selection: dict[str, Any] | None) -> list[str]:
    if not selection:
        return []
    selected_sections = selection.get("selected_sections", [])
    if not selected_sections:
        return []
    section_root = selection.get("selected_section_root")
    sections = [
        "## Selected Section Sources",
        "- 下記は内部的に参照する split section files。",
        "- 参照行ではこれらの path ではなく `## Citation Filenames` の論理 path を使うこと。",
    ]
    if section_root:
        sections.append(f"- Split source root: {section_root}")
    for entry in selected_sections:
        citation_file = entry.get("citation_file")
        section_names = entry.get("sections", [])
        section_files = entry.get("section_files", [])
        sections.append(f"- `{citation_file}`:")
        if section_names:
            sections.append(f"  sections: {', '.join(section_names)}")
        for path in section_files:
            sections.append(f"  - {path}")
    selected_count = selection.get("selected_section_count")
    if selected_count is not None:
        sections.extend(["", f"Selected section file count: {selected_count}"])
    return sections


def load_prompt_sections(
    input_text: str,
    mode: str,
    profile: ExtractProfileConfig | None = None,
) -> list[str]:
    if mode == "extract":
        shared_fragment = "extract_shared.md" if profile is None else profile.extract_prompt_fragment
        sections = [load_prompt_fragment(shared_fragment)]
        template_name = resolve_extract_template(input_text)
        sections.append(load_prompt_fragment(resolve_extract_template_fragment(template_name, profile)))
        return sections
    return [load_prompt_fragment("general.md")]


def build_prompt_text(
    input_text: str,
    mode: str,
    input_label: str,
    selection: dict[str, Any] | None = None,
    profile: ExtractProfileConfig | None = None,
) -> str:
    prompt_sections = load_prompt_sections(input_text, mode, profile)
    project_root = repo_root()
    mode_notice = f"[MODE:{mode.upper()}]"

    sections = [
        "# iching-sdk execution prompt",
        "## Runtime Context",
        f"- Runtime project: {project_root}",
        f"- CLI entry: {project_root / 'iching'}",
        f"- Sources root: {project_root / 'sources'}",
        f"- Rules root: {project_root / 'rules'}",
        f"- Prompts root: {project_root / 'prompts'}",
        f"- Input source: {input_label}",
        f"- Resolved mode: {mode}",
        f"- Resolved profile: {profile.name if profile is not None else 'legacy'}",
        "- Use only local Markdown files under sources/ as evidence unless the user explicitly asks otherwise.",
        "- The local CLI can be used for index lookup and validation.",
        "- This prompt is generated by iching-sdk; keep durable workflow logic in the SDK project.",
        "",
        "## Mode Override",
        mode_notice,
    ]

    selected_sections = format_selected_sources(selection)
    if selected_sections:
        sections.extend(["", *selected_sections])
    citation_sections = format_citation_filenames(mode, selection)
    if citation_sections:
        sections.extend(["", *citation_sections])
    section_source_sections = format_selected_section_sources(selection)
    if section_source_sections:
        sections.extend(["", *section_source_sections])

    sections.extend(
        [
            "",
            "## Prompt Instructions",
            "\n\n".join(prompt_sections),
            "",
            "## User Input",
            input_text.rstrip(),
            "",
        ]
    )
    return "\n".join(sections)


def load_prompt_input(input_arg: str) -> tuple[str, str]:
    return read_input_text(input_arg)

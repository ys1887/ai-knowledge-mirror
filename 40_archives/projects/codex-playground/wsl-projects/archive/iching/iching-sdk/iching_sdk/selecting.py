from __future__ import annotations

from typing import Any

from iching_sdk.config import (
    ExtractProfileConfig,
    RuntimeConfig,
    load_mode_config,
    load_runtime_config,
    resolve_profile_config,
    resolve_profile_extract_root,
)
from iching_sdk.indexing import parse_index
from iching_sdk.profiles import SplitHexagramSource, load_split_catalog
from iching_sdk.resolving import resolve_input_text


def list_indexed_files(
    mode: str,
    profile: ExtractProfileConfig,
    sources_root_override: str | None,
) -> list[str]:
    config = load_mode_config(mode, sources_root_override, profile if mode == "extract" else None)
    if mode != "extract" or profile.extract_source_kind == "legacy":
        return parse_index(config)
    if profile.extract_source_kind == "split":
        catalog = load_split_catalog(config.sources_root)
        return [catalog[number].source_file for number in sorted(catalog)]
    return []


def indexed_files_by_mode(
    profile: ExtractProfileConfig,
    sources_root_override: str | None,
) -> dict[str, list[str]]:
    return {
        mode: list_indexed_files(mode, profile, sources_root_override)
        for mode in ("extract", "general")
    }


def filter_extract_files_by_hexagram(
    extract_files: list[str],
    provider_prefix: str,
    hexagram_numbers: list[int],
) -> list[str]:
    if not hexagram_numbers:
        return [path for path in extract_files if path.startswith(provider_prefix)]
    selected_by_number: dict[int, str] = {}
    for path in extract_files:
        if not path.startswith(provider_prefix):
            continue
        filename = path.removeprefix(provider_prefix)
        try:
            number = int(filename.split("_", 1)[0])
        except (ValueError, IndexError):
            continue
        if number not in hexagram_numbers:
            continue
        selected_by_number[number] = path
    return [selected_by_number[number] for number in hexagram_numbers if number in selected_by_number]


def select_group_files(
    group_name: str,
    resolved: dict[str, Any],
    files_by_mode: dict[str, list[str]],
) -> list[str]:
    hexagram_numbers = resolved.get("hexagram_numbers", [])
    if group_name == "general_core":
        return list(files_by_mode["general"])
    if group_name == "extract_honda":
        return filter_extract_files_by_hexagram(
            files_by_mode["extract"], "honda_wataru/", hexagram_numbers
        )
    if group_name == "extract_takashima":
        return filter_extract_files_by_hexagram(
            files_by_mode["extract"], "takashima_zouho/", hexagram_numbers
        )
    return []


def flatten_selected_files(selected_groups: list[dict[str, Any]]) -> list[str]:
    selected_files: list[str] = []
    seen: set[str] = set()
    for group in selected_groups:
        for path in group["files"]:
            if path in seen:
                continue
            seen.add(path)
            selected_files.append(path)
    return selected_files


def _required_sections_for_split_template(
    resolved: dict[str, Any],
    hexagram_number: int,
    changing_lines: list[int],
) -> list[str]:
    template = resolved.get("template")
    sections: list[str] = []
    if template == "EX_COMPARE":
        sections.extend(["kaji", "taisho"])
    else:
        sections.extend(["kaji", "tanden", "taisho"])
    if template == "EX_5" and resolved.get("hexagram_numbers", [])[:1] != [hexagram_number]:
        return sections
    for line_number in changing_lines:
        sections.append(f"yao_{line_number}")
    return sections


def _candidate_changing_lines_by_hexagram(resolved: dict[str, Any]) -> dict[int, list[int]]:
    candidates = resolved.get("compare_candidates", [])
    if not isinstance(candidates, list):
        return {}
    mapping: dict[int, list[int]] = {}
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        raw_number = candidate.get("hexagram_number")
        raw_lines = candidate.get("changing_lines", [])
        if not isinstance(raw_number, int):
            continue
        if not isinstance(raw_lines, list) or not all(isinstance(line, int) for line in raw_lines):
            continue
        mapping[raw_number] = list(raw_lines)
    return mapping


def _build_split_selected_sections(
    resolved: dict[str, Any],
    catalog: dict[int, SplitHexagramSource],
) -> list[dict[str, Any]]:
    selected_sections: list[dict[str, Any]] = []
    compare_lines = _candidate_changing_lines_by_hexagram(resolved)
    primary_hexagram = resolved.get("hexagram_numbers", [None])[0]

    for hexagram_number in resolved.get("hexagram_numbers", []):
        source = catalog.get(hexagram_number)
        if source is None:
            continue

        if resolved.get("template") == "EX_COMPARE":
            changing_lines = compare_lines.get(hexagram_number, [])
        elif resolved.get("template") == "EX_5" and hexagram_number != primary_hexagram:
            changing_lines = []
        else:
            raw_lines = resolved.get("changing_lines", [])
            changing_lines = raw_lines if isinstance(raw_lines, list) else []

        section_names = _required_sections_for_split_template(resolved, hexagram_number, changing_lines)
        section_files: list[str] = []
        existing_sections: list[str] = []
        for section_name in section_names:
            section_file = source.sections.get(section_name)
            if section_file is None:
                continue
            existing_sections.append(section_name)
            section_files.append(f"{source.folder_name}/{section_file}")
        selected_sections.append(
            {
                "hexagram_number": source.number,
                "citation_file": source.source_file,
                "sections": existing_sections,
                "section_files": section_files,
            }
        )
    return selected_sections


def _build_split_selection(
    resolved: dict[str, Any],
    profile: ExtractProfileConfig,
    sources_root_override: str | None,
) -> dict[str, Any]:
    root = resolve_profile_extract_root(profile, sources_root_override)
    catalog = load_split_catalog(root)
    selected_sections = _build_split_selected_sections(resolved, catalog)
    group_name = profile.extract_groups[0]
    selected_groups = [
        {
            "group": group_name,
            "files": [entry["citation_file"] for entry in selected_sections],
            "section_files": [
                path for entry in selected_sections for path in entry.get("section_files", [])
            ],
        }
    ]
    selected_files = flatten_selected_files(selected_groups)
    selected_section_files = flatten_selected_files(
        [{"files": group["section_files"]} for group in selected_groups]
    )
    return {
        **resolved,
        "selected_groups": selected_groups,
        "selected_files": selected_files,
        "selected_file_count": len(selected_files),
        "selected_sections": selected_sections,
        "selected_section_root": str(root),
        "selected_section_files": selected_section_files,
        "selected_section_count": len(selected_section_files),
    }


def select_input_text(
    input_arg: str,
    override_mode: str | None,
    sources_root_override: str | None = None,
    profile_name: str | None = None,
    runtime_config: RuntimeConfig | None = None,
) -> dict[str, Any]:
    active_runtime_config = load_runtime_config() if runtime_config is None else runtime_config
    profile = resolve_profile_config(active_runtime_config, profile_name)
    resolved = resolve_input_text(input_arg, override_mode, profile)
    return select_resolved_input(
        resolved,
        sources_root_override=sources_root_override,
        profile_name=profile_name,
        runtime_config=active_runtime_config,
    )


def select_resolved_input(
    resolved: dict[str, Any],
    sources_root_override: str | None = None,
    profile_name: str | None = None,
    runtime_config: RuntimeConfig | None = None,
) -> dict[str, Any]:
    active_runtime_config = load_runtime_config() if runtime_config is None else runtime_config
    profile = resolve_profile_config(
        active_runtime_config,
        profile_name or resolved.get("profile"),
    )
    if resolved.get("mode") == "extract" and profile.extract_source_kind == "split":
        return _build_split_selection(resolved, profile, sources_root_override)

    files_by_mode = indexed_files_by_mode(profile, sources_root_override)
    selected_groups = [
        {
            "group": group_name,
            "files": select_group_files(group_name, resolved, files_by_mode),
        }
        for group_name in resolved["source_groups"]
    ]
    selected_files = flatten_selected_files(selected_groups)
    return {
        **resolved,
        "selected_groups": selected_groups,
        "selected_files": selected_files,
        "selected_file_count": len(selected_files),
    }

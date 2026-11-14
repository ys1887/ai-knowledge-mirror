from __future__ import annotations

from typing import Any

from iching_sdk.config import load_mode_config
from iching_sdk.indexing import parse_index
from iching_sdk.resolving import resolve_input_text


def indexed_files_by_mode(sources_root_override: str | None) -> dict[str, list[str]]:
    return {
        mode: parse_index(load_mode_config(mode, sources_root_override))
        for mode in ("extract", "general")
    }


def select_group_files(
    group_name: str,
    resolved: dict[str, Any],
    files_by_mode: dict[str, list[str]],
) -> list[str]:
    if group_name == "general_core":
        return list(files_by_mode["general"])
    if group_name == "extract_support":
        if resolved["input_kind"] == "general_comparison":
            return list(files_by_mode["extract"])
        return []
    if group_name == "extract_honda":
        return [
            path for path in files_by_mode["extract"] if path.startswith("honda_wataru/")
        ]
    if group_name == "extract_takashima":
        return [
            path for path in files_by_mode["extract"] if path.startswith("takashima_zouho/")
        ]
    if group_name == "general_support":
        return list(files_by_mode["general"])
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


def select_input_text(
    input_arg: str,
    override_mode: str | None,
    sources_root_override: str | None = None,
) -> dict[str, Any]:
    resolved = resolve_input_text(input_arg, override_mode)
    return select_resolved_input(resolved, sources_root_override)


def select_resolved_input(
    resolved: dict[str, Any],
    sources_root_override: str | None = None,
) -> dict[str, Any]:
    files_by_mode = indexed_files_by_mode(sources_root_override)
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

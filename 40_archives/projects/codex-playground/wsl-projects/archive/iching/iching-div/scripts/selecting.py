from __future__ import annotations

from typing import Any

from indexing import SplitSource, load_split_catalog
from profiles import ProfileConfig, ProviderConfig, ValidationError


HONDA_SUPPORTABLE_BUNGEN_HEXAGRAMS = {1, 2}


def _required_sections(template: str, is_primary: bool, changing_lines: list[int]) -> list[str]:
    sections = ["kaji", "tanden", "taisho"]
    if template == "EX_COMPARE":
        sections = ["kaji", "taisho"]
    if not is_primary and template == "EX_5":
        return sections
    for line_number in changing_lines:
        sections.append(f"yao_{line_number}")
    return sections


def _provider_item(
    provider: ProviderConfig,
    source: SplitSource,
    section_names: list[str],
    role: str,
    candidate_label: str | None = None,
    output_visibility: str = "normal",
) -> dict[str, Any]:
    section_paths = [
        str(provider.asset_root / source.folder_name / source.sections[section_name])
        for section_name in section_names
        if section_name in source.sections
    ]
    available_sections = [section_name for section_name in section_names if section_name in source.sections]
    if not available_sections:
        raise ValidationError(
            f"required sections not found for {provider.name}:{source.number}:{role}"
        )
    return {
        "provider": provider.name,
        "interpretation_label": provider.interpretation_label,
        "hexagram_number": source.number,
        "hexagram_name": source.name,
        "citation_file": source.source_file,
        "section_names": available_sections,
        "section_paths": section_paths,
        "role": role,
        "candidate_label": candidate_label,
        "output_visibility": output_visibility,
    }


def _support_section_names(
    profile: ProfileConfig,
    provider: ProviderConfig,
    template: str,
    role: str,
    hexagram_number: int,
) -> list[str]:
    if profile.name != "honda" or provider.name != "honda":
        return []
    if template == "EX_COMPARE":
        return []

    support_names: list[str] = []
    if template == "EX_5" and role in {"main_hexagram", "auxiliary_hexagram"}:
        support_names.append("jokaden")
    if hexagram_number in HONDA_SUPPORTABLE_BUNGEN_HEXAGRAMS:
        if template == "EX_SIMPLE" and role == "main_hexagram":
            support_names.append("bungen")
        elif template == "EX_5" and role in {"main_hexagram", "auxiliary_hexagram"}:
            support_names.append("bungen")
    return support_names


def _support_item(
    profile: ProfileConfig,
    provider: ProviderConfig,
    source: SplitSource,
    template: str,
    role: str,
) -> dict[str, Any] | None:
    support_names = [
        name for name in _support_section_names(profile, provider, template, role, source.number)
        if name in source.sections
    ]
    if not support_names:
        return None
    return {
        "provider": provider.name,
        "interpretation_label": provider.interpretation_label,
        "hexagram_number": source.number,
        "hexagram_name": source.name,
        "role": role,
        "support_section_names": support_names,
        "support_section_paths": [
            str(provider.asset_root / source.folder_name / source.sections[name])
            for name in support_names
        ],
        "usage_scope": "final_honda_interpretation_only",
    }


def _select_standard_or_ex5(
    profile: ProfileConfig,
    resolved: dict[str, Any],
    catalogs: dict[str, dict[int, SplitSource]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    template = resolved["template"]
    main_number = resolved["main_hexagram_number"]
    changing_lines = resolved["changing_lines"]
    auxiliary_numbers = {item["hexagram_number"] for item in resolved.get("auxiliary_hexagrams", [])}
    selected: list[dict[str, Any]] = []
    support_items: list[dict[str, Any]] = []
    for provider in profile.providers:
        catalog = catalogs[provider.name]
        for number in resolved["hexagram_numbers"]:
            source = catalog.get(number)
            if source is None:
                raise ValidationError(f"hexagram {number} not found in {provider.name} split assets")
            is_primary = number == main_number and number not in auxiliary_numbers
            item_role = "main_hexagram" if is_primary else "auxiliary_hexagram"
            item_lines = changing_lines if is_primary else []
            selected.append(
                _provider_item(
                    provider,
                    source,
                    _required_sections(template, is_primary, item_lines),
                    role=item_role,
                )
            )
            support_item = _support_item(profile, provider, source, template, item_role)
            if support_item is not None:
                support_items.append(support_item)
    return selected, support_items


def _select_compare(
    profile: ProfileConfig,
    resolved: dict[str, Any],
    catalogs: dict[str, dict[int, SplitSource]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    for provider in profile.providers:
        catalog = catalogs[provider.name]
        for candidate in resolved["compare_candidates"]:
            number = candidate["hexagram_number"]
            source = catalog.get(number)
            if source is None:
                raise ValidationError(f"hexagram {number} not found in {provider.name} split assets")
            visibility = "normal"
            if provider.name == "takashima" and profile.compare_takashima_support_only:
                visibility = "support_only"
            selected.append(
                _provider_item(
                    provider,
                    source,
                    _required_sections("EX_COMPARE", True, candidate["changing_lines"]),
                    role="candidate_detail",
                    candidate_label=candidate["label"],
                    output_visibility=visibility,
                )
            )
    return selected, []


def select_sources(profile: ProfileConfig, resolved: dict[str, Any]) -> dict[str, Any]:
    catalogs = {provider.name: load_split_catalog(provider) for provider in profile.providers}
    if resolved["template"] == "EX_COMPARE":
        items, support_items = _select_compare(profile, resolved, catalogs)
    else:
        items, support_items = _select_standard_or_ex5(profile, resolved, catalogs)

    citation_files: list[str] = []
    seen_citations: set[str] = set()
    section_paths: list[str] = []
    seen_sections: set[str] = set()
    for item in items:
        citation_file = item["citation_file"]
        if citation_file not in seen_citations:
            seen_citations.add(citation_file)
            citation_files.append(citation_file)
        for path in item["section_paths"]:
            if path in seen_sections:
                continue
            seen_sections.add(path)
            section_paths.append(path)

    support_section_paths: list[str] = []
    seen_support_sections: set[str] = set()
    for item in support_items:
        for path in item["support_section_paths"]:
            if path in seen_support_sections:
                continue
            seen_support_sections.add(path)
            support_section_paths.append(path)

    return {
        **resolved,
        "profile": profile.name,
        "final_sections": list(profile.final_sections),
        "selected_items": items,
        "support_items": support_items,
        "citation_files": citation_files,
        "section_paths": section_paths,
        "support_section_paths": support_section_paths,
    }

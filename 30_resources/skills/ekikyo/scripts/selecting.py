from __future__ import annotations

from typing import Literal, TypedDict

from indexing import TakashimaSource, load_takashima_catalog
from profiles import ProviderConfig, ValidationError
from resolving import CompareResolved, ResolvedBase, ResolvedInput, StandardResolved


class SelectedItem(TypedDict):
    provider: str
    interpretation_label: str
    hexagram_number: int
    hexagram_name: str
    citation_file: str
    section_names: list[str]
    section_paths: list[str]
    role: Literal["main_hexagram", "auxiliary_hexagram", "candidate_detail"]
    candidate_label: str | None


class SelectionResult(ResolvedBase):
    template: Literal["EX_SIMPLE", "EX_SIMPLE2", "EX_5", "EX_COMPARE"]
    selected_items: list[SelectedItem]
    support_items: list[object]
    citation_files: list[str]
    section_paths: list[str]
    support_section_paths: list[str]


def _required_sections(template: str, is_primary: bool, changing_lines: list[int]) -> list[str]:
    sections = ["kaji", "tanden", "taisho"]
    if template == "EX_COMPARE":
        sections = []
    if not is_primary and template in ("EX_SIMPLE2", "EX_5"):
        return sections
    for line_number in changing_lines:
        sections.append(f"yao_{line_number}")
    return sections


def _provider_item(
    provider: ProviderConfig,
    source: TakashimaSource,
    section_names: list[str],
    role: Literal["main_hexagram", "auxiliary_hexagram", "candidate_detail"],
    candidate_label: str | None = None,
) -> SelectedItem:
    if not source.file_path.is_file():
        raise ValidationError(f"missing source file: {source.file_path}")
    return {
        "provider": provider.name,
        "interpretation_label": provider.interpretation_label,
        "hexagram_number": source.number,
        "hexagram_name": source.name,
        "citation_file": source.source_file,
        "section_names": section_names,
        "section_paths": [str(source.file_path)],
        "role": role,
        "candidate_label": candidate_label,
    }


def _select_standard_or_ex5(
    resolved: StandardResolved,
    catalog: dict[int, TakashimaSource],
    provider: ProviderConfig,
) -> list[SelectedItem]:
    template = resolved["template"]
    main_number = resolved["main_hexagram_number"]
    changing_lines = resolved["changing_lines"]
    auxiliary_numbers = {item["hexagram_number"] for item in resolved.get("auxiliary_hexagrams", [])}
    selected: list[SelectedItem] = []
    for number in resolved["hexagram_numbers"]:
        source = catalog.get(number)
        if source is None:
            raise ValidationError(f"hexagram {number} not found in {provider.name} source files")
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
    return selected


def _select_compare(
    resolved: CompareResolved,
    catalog: dict[int, TakashimaSource],
    provider: ProviderConfig,
) -> list[SelectedItem]:
    selected: list[SelectedItem] = []
    for candidate in resolved["compare_candidates"]:
        number = candidate["hexagram_number"]
        source = catalog.get(number)
        if source is None:
            raise ValidationError(f"hexagram {number} not found in {provider.name} source files")
        selected.append(
            _provider_item(
                provider,
                source,
                _required_sections("EX_COMPARE", True, candidate["changing_lines"]),
                role="candidate_detail",
                candidate_label=candidate["label"],
            )
        )
    return selected


def select_sources(provider: ProviderConfig, resolved: ResolvedInput) -> SelectionResult:
    if provider.name != "takashima":
        raise ValidationError("takashima provider is the only supported provider in this repository.")

    catalog = load_takashima_catalog(provider)
    if resolved["template"] == "EX_COMPARE":
        items = _select_compare(resolved, catalog, provider)
    else:
        items = _select_standard_or_ex5(resolved, catalog, provider)

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

    return {
        **resolved,
        "selected_items": items,
        "support_items": [],
        "citation_files": citation_files,
        "section_paths": section_paths,
        "support_section_paths": [],
    }

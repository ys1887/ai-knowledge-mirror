from __future__ import annotations

from typing import Any

from iching_sdk.prompting import (
    EXTRACT_COMPARE_MARKER,
    detect_mode,
    load_prompt_input,
)


EXTRACT_TEMPLATE_MARKERS = ("[TEMPLATE:EX_SIMPLE]", "[TEMPLATE:EX_5]", EXTRACT_COMPARE_MARKER)
COMPARISON_HINTS = (
    "比較",
    "候補",
    "オススメ",
    "おすすめ",
    "順位",
    "ランキング",
)
RANKING_HINTS = (
    "順番",
    "順位",
    "ランキング",
    "オススメ",
    "おすすめ",
)


def detect_input_kind(mode: str, text: str) -> str:
    if mode == "extract":
        if EXTRACT_COMPARE_MARKER in text:
            return "extract_comparison"
        return "extract_template"
    if any(marker in text for marker in COMPARISON_HINTS):
        return "general_comparison"
    return "general_question"


def build_source_groups(mode: str) -> list[str]:
    if mode == "extract":
        return ["extract_honda", "extract_takashima", "general_support"]
    return ["general_core", "extract_support"]


def build_hints(mode: str, text: str, input_kind: str) -> list[str]:
    hints: list[str] = []
    if mode == "extract":
        hints.append("requires_strict_citation")
        if any(marker in text for marker in EXTRACT_TEMPLATE_MARKERS):
            hints.append("template_marker_present")
    if input_kind in {"general_comparison", "extract_comparison"}:
        hints.append("comparison_requested")
        if any(marker in text for marker in RANKING_HINTS):
            hints.append("ranking_requested")
    return hints


def resolve_loaded_input(
    input_source: str, input_text: str, override_mode: str | None
) -> dict[str, Any]:
    mode = override_mode or detect_mode(input_text)
    input_kind = detect_input_kind(mode, input_text)
    return {
        "mode": mode,
        "input_source": input_source,
        "input_kind": input_kind,
        "source_groups": build_source_groups(mode),
        "hints": build_hints(mode, input_text, input_kind),
    }


def resolve_input_text(input_arg: str, override_mode: str | None) -> dict[str, Any]:
    input_source, input_text = load_prompt_input(input_arg)
    return resolve_loaded_input(input_source, input_text, override_mode)

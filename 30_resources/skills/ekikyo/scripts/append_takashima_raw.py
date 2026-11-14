from __future__ import annotations

import argparse
import sys
from pathlib import Path

from indexing import load_takashima_catalog
from profiles import ValidationError, takashima_provider
from rendering import (
    build_ex_5_takashima_raw_text,
    build_ex_simple2_takashima_raw_text,
    build_ex_simple_takashima_raw_text,
    build_reference_case_excerpt_section,
)
from resolving import ResolvedInput, resolve_input
from workflow import line_label_from_numbers, line_labels_from_numbers


def _read_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"input file not found: {path}")
    return path.read_text(encoding="utf-8")


def _read_answer_text(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"answer file not found: {path}")
    return path.read_text(encoding="utf-8")


def _append_reference_case_excerpt(raw_text: str, hexagram_number: int, line_label: str) -> str:
    if not line_label:
        return raw_text
    excerpt_section = build_reference_case_excerpt_section(hexagram_number, line_label)
    if not excerpt_section:
        return raw_text
    if raw_text and not raw_text.endswith("\n"):
        raw_text += "\n"
    return raw_text + "\n" + excerpt_section


def _build_raw_text(input_path: Path) -> str:
    provider = takashima_provider()
    catalog = load_takashima_catalog(provider)
    resolved: ResolvedInput = resolve_input(_read_text(input_path))
    if resolved["template"] == "EX_COMPARE":
        raise ValidationError("append raw section not supported for EX_COMPARE")

    if resolved["template"] == "EX_SIMPLE":
        main_source = catalog[resolved["main_hexagram_number"]]
        line_label = line_label_from_numbers(resolved["changing_lines"])
        raw_text = build_ex_simple_takashima_raw_text(main_source.file_path, line_label)
        return _append_reference_case_excerpt(raw_text, main_source.number, line_label)

    if resolved["template"] == "EX_SIMPLE2":
        main_source = catalog[resolved["main_hexagram_number"]]
        line_label = line_label_from_numbers(resolved["changing_lines"])
        zhigua = next(item for item in resolved["auxiliary_hexagrams"] if item["label"] == "之卦")
        zhigua_source = catalog[zhigua["hexagram_number"]]
        raw_text = build_ex_simple2_takashima_raw_text(
            main_path=main_source.file_path,
            line_label=line_label,
            zhigua_path=zhigua_source.file_path,
            zhigua_heading_suffix=f"（{zhigua_source.number} {zhigua_source.name}）",
        )
        return _append_reference_case_excerpt(raw_text, main_source.number, line_label)

    main_source = catalog[resolved["main_hexagram_number"]]
    line_labels = line_labels_from_numbers(resolved["changing_lines"])
    line_label = line_labels[0] if len(line_labels) == 1 else ""
    zhigua_path = None
    zhigua_heading_suffix = None
    auxiliary_items: list[tuple[str, Path, str]] = []
    for item in resolved.get("auxiliary_hexagrams", []):
        source = catalog[item["hexagram_number"]]
        heading_suffix = f"（{source.number} {source.name}）"
        if item["label"] == "之卦":
            zhigua_path = source.file_path
            zhigua_heading_suffix = heading_suffix
            continue
        auxiliary_items.append((item["label"], source.file_path, heading_suffix))
    raw_text = build_ex_5_takashima_raw_text(
        main_path=main_source.file_path,
        main_heading_suffix=f"（{main_source.number} {main_source.name}）",
        line_labels=line_labels,
        zhigua_path=zhigua_path,
        zhigua_heading_suffix=zhigua_heading_suffix,
        auxiliary_items=auxiliary_items,
    )
    return _append_reference_case_excerpt(raw_text, main_source.number, line_label)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Append Takashima raw text to an answer file.")
    parser.add_argument("--input", required=True, help="Input file path.")
    parser.add_argument("--output", required=True, help="Output file path.")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)
    try:
        raw_text = _build_raw_text(input_path)
        content = _read_answer_text(output_path)
        if content:
            content = content.rstrip("\n")
            content += "\n\n\n" + raw_text.lstrip("\n")
        else:
            content = raw_text
        output_path.write_text(content, encoding="utf-8")
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

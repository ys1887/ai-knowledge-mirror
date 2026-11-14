from __future__ import annotations

import argparse
import sys
from pathlib import Path

from indexing import load_takashima_catalog
from profiles import ValidationError, canonical_quotes_root, load_format, repo_root, takashima_provider
from rendering import (
    load_honka_quotes,
    load_line_quotes,
    load_reference_case_excerpt_text,
    load_takashima_honka_text,
    load_takashima_line_text,
)
from resolving import resolve_input
from selecting import SelectionResult, select_sources
from workflow import line_label_from_numbers, line_labels_from_numbers


def _read_input(path_arg: str) -> str:
    if path_arg == "-":
        return sys.stdin.read()
    path = Path(path_arg)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"input file not found: {path}") from exc


def _build_runtime_lines(selection: SelectionResult, input_label: str) -> list[str]:
    return [
        "# ekikyo takashima-source execution prompt",
        "## Runtime Contract",
        f"- Project root: {repo_root()}",
        f"- Input source: {input_label}",
        "- Source family: takashima only",
        f"- Mode: {selection['mode']}",
        f"- Template: {selection['template']}",
        "- This prompt was built by the preprocessing script only.",
        "- Final answer `## 参照` section must use citation paths only.",
        "- Section paths are internal file paths and must never appear in the final answer.",
        "- Canonical answers are structural references only, not literal target text.",
    ]


def _build_canonical_source_lines() -> list[str]:
    lines = [
        "## Canonical Source Roots",
        f"- Shared quotes: {canonical_quotes_root()}",
        f"- takashima interpretation: {repo_root() / 'assets' / 'takashima'}",
    ]
    return lines


def _build_quality_bar_lines(selection: SelectionResult) -> list[str]:
    lines = [
        "## Output Quality Bar",
        "- Produce a polished Japanese answer for the end user, not a preprocessing summary.",
        "- Follow the required section order exactly for the active template.",
        "- The final answer begins with a machine-copied `## 質問文` section built from the user input; write prose only in `**核心・結論**`, template-required auxiliary interpretation headings, and `## 総合解釈`.",
        "- Keep citation paths and internal section paths impossible to confuse in the final answer.",
        "- Treat canonical answers as shape references only.",
        "- Use only the Takashima source family.",
    ]
    return lines


def _build_selection_lines(selection: SelectionResult) -> list[str]:
    lines = [
        "## Citation Paths",
        "- Use only the following relative citation paths in the final-answer `## 参照` section.",
    ]
    lines.extend(f"- `{path}`" for path in selection["citation_files"])
    lines.extend(
        [
            "",
            "## Section Paths (Internal Only)",
            "- These are internal evidence paths for lookup only.",
            "- Do not expose these paths in the final answer.",
        ]
    )
    lines.extend(f"- `{path}`" for path in selection["section_paths"])
    lines.extend(["", "## Selected Source Plan"])
    for item in selection["selected_items"]:
        detail = f"- provider={item['provider']} role={item['role']} number={item['hexagram_number']}"
        if item.get("candidate_label"):
            detail += f" candidate={item['candidate_label']}"
        lines.append(detail)
        lines.append(f"  citation: `{item['citation_file']}`")
        lines.append(f"  sections: {', '.join(item['section_names'])}")
    return lines


def _build_format_lines(selection: SelectionResult) -> list[str]:
    sections = [
        "## Shared Format Rules",
        load_format("shared.md"),
        "",
        "## Template Rules",
        load_format(f"{selection['template'].lower()}_single.md"),
    ]
    return sections


def _extract_section_between_markers(text: str, start_marker: str, end_marker: str | None) -> str:
    lines = text.splitlines()
    start_index = None
    end_index = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if start_index is None and stripped == start_marker:
            start_index = index + 1
            continue
        if start_index is not None and end_marker is not None and stripped == end_marker:
            end_index = index
            break
    if start_index is None:
        return ""
    if end_index is None:
        end_index = len(lines)
    return "\n".join(lines[start_index:end_index]).strip()


def _build_quote_section(title: str, quotes: object, interpretation_text: str | None = None) -> list[str]:
    lines = [title, "", quotes.raw_text]
    if interpretation_text:
        lines.extend(["", interpretation_text])
    return lines


def _build_occupation_reference_lines(number: int, line_label: str) -> list[str]:
    excerpt_text = load_reference_case_excerpt_text(number, line_label)
    if not excerpt_text:
        return []
    return [
        "## 占例参考",
        "",
        "- 以下は他者の占例であり、出典として引用・再構成するためのものではありません。",
        "- `## 総合解釈` では、判断の流れと結論の運び方を学ぶ参考としてのみ読みます。",
        "",
        f"### 対応する変爻：{line_label}",
        "",
        excerpt_text.rstrip(),
    ]


def _build_evidence_lines(input_text: str, selection: SelectionResult) -> list[str]:
    provider = takashima_provider()
    catalog = load_takashima_catalog(provider)
    lines: list[str] = [f"- template: {selection['template']}", ""]
    lines.extend(["## 背景", _extract_section_between_markers(input_text, "### 1. 占いに至った背景・状況", "### 2. 易経への質問"), ""])
    lines.extend(["## 易経への質問", _extract_section_between_markers(input_text, "### 2. 易経への質問", "### 3. 占い結果入力"), ""])

    if selection["template"] == "EX_COMPARE":
        lines.append("## 比較候補")
        for index, candidate in enumerate(selection["compare_candidates"], start=1):
            source = catalog[candidate["hexagram_number"]]
            heading = f"## 候補{index}：{candidate['label']}（{source.number} {source.name}）"
            line_label = line_label_from_numbers(candidate["changing_lines"])
            if line_label:
                line_quotes = load_line_quotes(source.number, line_label)
                lines.extend([heading, ""])
                lines.extend(
                    [
                        f"### 爻辞",
                        "",
                        f"> {line_quotes.koji.original}",
                        f"> {line_quotes.koji.reading}",
                    ]
                )
                if line_quotes.shozoden is not None:
                    lines.extend(
                        [
                            "",
                            "### 小象伝",
                            "",
                            f"> {line_quotes.shozoden.original}",
                            f"> {line_quotes.shozoden.reading}",
                        ]
                    )
                lines.append("")
        return lines

    main_source = catalog[selection["main_hexagram_number"]]
    main_quotes = load_honka_quotes(main_source.number)
    main_text = load_takashima_honka_text(main_source.file_path)
    lines.extend(_build_quote_section(f"## 本卦（{main_source.number} {main_source.name}）", main_quotes, "\n\n".join(main_text.values())))
    lines.append("")

    for line_label in line_labels_from_numbers(selection["changing_lines"]):
        line_quotes = load_line_quotes(main_source.number, line_label)
        line_text = load_takashima_line_text(main_source.file_path, line_label)
        lines.extend(_build_quote_section(f"## 変爻（{line_label}）", line_quotes, line_text))
        lines.append("")
        reference_lines = _build_occupation_reference_lines(main_source.number, line_label)
        if reference_lines:
            lines.extend(reference_lines)
            lines.append("")

    if selection["template"] in ("EX_SIMPLE2", "EX_5"):
        for item in selection.get("auxiliary_hexagrams", []):
            source = catalog[item["hexagram_number"]]
            quotes = load_honka_quotes(source.number)
            text = load_takashima_honka_text(source.file_path)
            lines.extend(_build_quote_section(f"## {item['label']}（{source.number} {source.name}）", quotes, "\n\n".join(text.values())))
            lines.append("")

    return lines


def _build_evidence_bundle_text(input_text: str, selection: SelectionResult) -> str:
    lines = ["# ekikyo Evidence Bundle", *_build_evidence_lines(input_text, selection)]
    return "\n".join(lines).rstrip() + "\n"


def _build_prompt_evidence_lines(input_text: str, selection: SelectionResult) -> list[str]:
    if selection["template"] == "EX_COMPARE":
        return []
    return [
        "## Source Evidence",
        "- Use the following script-extracted quote blocks and Takashima passages when writing `**核心・結論**`, template-required auxiliary interpretation headings, and `## 総合解釈`.",
        "- Quote blocks are fixed source blocks assembled later by script; do not regenerate them in the answer body except for short inline quotations or close paraphrases inside prose.",
        "",
        *_build_evidence_lines(input_text, selection),
    ]


def build_prompt_text(input_text: str, input_label: str) -> str:
    resolved = resolve_input(input_text)
    selection: SelectionResult = select_sources(takashima_provider(), resolved)
    lines = []
    lines.extend(_build_runtime_lines(selection, input_label))
    lines.extend(["", *_build_canonical_source_lines()])
    lines.extend(["", *_build_quality_bar_lines(selection)])
    lines.extend(["", *_build_selection_lines(selection)])
    lines.extend(["", *_build_format_lines(selection)])
    prompt_evidence_lines = _build_prompt_evidence_lines(input_text, selection)
    if prompt_evidence_lines:
        lines.extend(["", *prompt_evidence_lines])
    lines.extend(
        [
            "",
            "## User Input",
            "```text",
            input_text.rstrip(),
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def build_evidence_bundle(input_text: str) -> str:
    resolved = resolve_input(input_text)
    selection: SelectionResult = select_sources(takashima_provider(), resolved)
    return _build_evidence_bundle_text(input_text, selection)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Takashima-source EXTRACT prompt text.")
    parser.add_argument("--input", required=True, help="Input file path or - for stdin.")
    parser.add_argument("--output-dir", help="If set, write an evidence bundle into this directory and print the path.")
    args = parser.parse_args(argv)

    try:
        input_text = _read_input(args.input)
        input_label = "stdin" if args.input == "-" else str(Path(args.input).resolve())
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / (f"{Path(args.input).stem}_evidence_bundle.md" if args.input != "-" else "stdin_evidence_bundle.md")
            output_path.write_text(build_evidence_bundle(input_text), encoding="utf-8")
            print(str(output_path.resolve()))
        else:
            sys.stdout.write(build_prompt_text(input_text, input_label))
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

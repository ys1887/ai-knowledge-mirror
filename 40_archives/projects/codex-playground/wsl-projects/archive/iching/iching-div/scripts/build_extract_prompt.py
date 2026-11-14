from __future__ import annotations

import argparse
import sys
from pathlib import Path

from profiles import (
    ValidationError,
    canonical_quotes_root,
    load_format,
    load_template_format,
    resolve_profile,
    repo_root,
)
from resolving import resolve_input
from selecting import select_sources


def _read_input(path_arg: str) -> str:
    if path_arg == "-":
        return sys.stdin.read()
    path = Path(path_arg)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"input file not found: {path}") from exc


def _build_runtime_lines(profile_name: str, selection: dict[str, object], input_label: str) -> list[str]:
    return [
        "# iching-div split-source execution prompt",
        "## Runtime Contract",
        f"- Project root: {repo_root()}",
        f"- Input source: {input_label}",
        f"- Profile: {profile_name}",
        f"- Mode: {selection['mode']}",
        f"- Template: {selection['template']}",
        "- This prompt was built by the preprocessing script only.",
        "- Final answer references must use citation paths only.",
        "- Section paths are internal lookup paths and must never appear in the final answer.",
        "- Canonical answers are structural references only, not literal target text.",
    ]


def _build_canonical_source_lines(profile_name: str) -> list[str]:
    profile = resolve_profile(profile_name)
    lines = [
        "## Canonical Source Roots",
        f"- Shared quotes: {canonical_quotes_root()}",
    ]
    for provider in profile.providers:
        lines.append(f"- {provider.name} interpretation: {provider.interpretation_root}")
    return lines


def _build_quality_bar_lines(selection: dict[str, object]) -> list[str]:
    lines = [
        "## Output Quality Bar",
        "- Produce a polished Japanese answer for the end user, not a preprocessing summary.",
        "- Follow the required section order exactly for the active template.",
        "- Keep citation paths and internal section paths impossible to confuse in the final answer.",
        "- Treat canonical answers as shape references only.",
    ]
    if selection["profile"] == "legacy" and selection["template"] == "EX_COMPARE":
        lines.append(
            "- In legacy compare mode, Honda leads the narrated candidate detail and Takashima remains support-only."
        )
    elif selection["profile"] == "legacy":
        lines.append(
            "- In legacy standard extract modes, keep both interpretation sections distinct and in fixed order."
        )
    else:
        lines.append(
            f"- In the {selection['profile']} profile, do not leak the other source family into interpretation requirements."
        )
    return lines


def _build_selection_lines(selection: dict[str, object]) -> list[str]:
    lines = [
        "## Citation Paths",
        "- Use only the following relative citation paths in final-answer reference lines.",
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
    support_items = selection.get("support_items", [])
    if support_items:
        lines.extend(
            [
                "",
                "## Honda Interpretation Support Paths (Internal Only)",
                "- These support-only paths are for `**本田解釈**` only.",
                "- They must never produce standalone `### 序卦伝` or `### 文言伝` headings.",
            ]
        )
        lines.extend(f"- `{path}`" for path in selection["support_section_paths"])
    lines.extend(["", "## Selected Source Plan"])
    for item in selection["selected_items"]:
        detail = f"- provider={item['provider']} role={item['role']} number={item['hexagram_number']}"
        if item.get("candidate_label"):
            detail += f" candidate={item['candidate_label']}"
        if item.get("output_visibility"):
            detail += f" visibility={item['output_visibility']}"
        lines.append(detail)
        lines.append(f"  citation: `{item['citation_file']}`")
        lines.append(f"  sections: {', '.join(item['section_names'])}")
    if support_items:
        lines.extend(["", "## Honda Interpretation Support Plan"])
        for item in support_items:
            lines.append(
                f"- provider={item['provider']} role={item['role']} number={item['hexagram_number']} "
                f"usage={item['usage_scope']}"
            )
            lines.append(f"  support sections: {', '.join(item['support_section_names'])}")
    return lines


def _build_format_lines(selection: dict[str, object]) -> list[str]:
    sections = [
        "## Shared Format Rules",
        load_format("shared.md"),
        "",
        "## Profile Rules",
        load_format(f"profile_{selection['profile']}.md"),
        "",
        "## Template Rules",
        load_template_format(selection["profile"], selection["template"]),
    ]
    return sections


def build_prompt_text(input_text: str, profile_name: str, input_label: str) -> str:
    profile = resolve_profile(profile_name)
    resolved = resolve_input(input_text)
    selection = select_sources(profile, resolved)
    lines = []
    lines.extend(_build_runtime_lines(profile_name, selection, input_label))
    lines.extend(["", *_build_canonical_source_lines(profile_name)])
    lines.extend(["", *_build_quality_bar_lines(selection)])
    lines.extend(["", * _build_selection_lines(selection)])
    lines.extend(["", * _build_format_lines(selection)])
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build split-source EXTRACT prompt text.")
    parser.add_argument("--input", required=True, help="Input file path or - for stdin.")
    parser.add_argument(
        "--profile",
        required=True,
        choices=("legacy", "honda", "takashima"),
        help="Fixed profile to apply.",
    )
    args = parser.parse_args(argv)

    try:
        input_text = _read_input(args.input)
        input_label = "stdin" if args.input == "-" else str(Path(args.input).resolve())
        sys.stdout.write(build_prompt_text(input_text, args.profile, input_label))
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

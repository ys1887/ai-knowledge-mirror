#!/usr/bin/env python3
"""Combine text-like files into grouped markdown outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple


SUPPORTED_INPUT_FORMATS = ("md", "txt", "json")


@dataclass(frozen=True)
class GroupPlan:
    index: int
    files: List[Path]
    suffix: str
    output_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Combine markdown files by grouping rules")
    parser.add_argument("--in-dir", required=True, help="Input directory containing source files")
    parser.add_argument("--out-dir", required=True, help="Output directory for merged files")
    parser.add_argument("--prefix", required=True, help="Output prefix for heading/file naming")
    parser.add_argument(
        "--input-format",
        choices=SUPPORTED_INPUT_FORMATS,
        default="md",
        help="Input file format to combine",
    )
    parser.add_argument(
        "--json-text-key",
        help="Root-level JSON key containing page text; required when --input-format=json",
    )
    parser.add_argument("--group-size", type=int, help="Group size for automatic grouping")
    parser.add_argument("--groups", help='Explicit 1-based ranges, e.g. "1-8,9-16"')
    parser.add_argument(
        "--name-mode",
        choices=["auto-range", "ordinal"],
        default="auto-range",
        help="Output suffix mode",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show planned outputs without writing files")
    return parser.parse_args()


def normalize_prefix(value: str) -> str:
    text = value.strip()
    if not text:
        raise ValueError("--prefix must not be empty")
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def validate_args(args: argparse.Namespace) -> None:
    if args.input_format == "json" and not args.json_text_key:
        raise ValueError("--json-text-key is required when --input-format=json")
    if args.input_format != "json" and args.json_text_key:
        raise ValueError("--json-text-key can only be used when --input-format=json")


def load_input_files(in_dir: Path, input_format: str) -> List[Path]:
    if not in_dir.exists() or not in_dir.is_dir():
        raise ValueError(f"Input directory not found: {in_dir}")
    suffix = f".{input_format}"
    files = [p for p in in_dir.iterdir() if p.is_file() and p.suffix.lower() == suffix]
    if not files:
        raise ValueError(f"No {suffix} files found in: {in_dir}")
    files.sort(key=natural_key)
    return files


def natural_key(path: Path) -> Tuple[int, str]:
    name = path.stem.lower()
    numbers = re.findall(r"\d+", name)
    first_num = int(numbers[0]) if numbers else 10**9
    return (first_num, name)


def build_groups(files: List[Path], group_size: Optional[int], groups_arg: Optional[str]) -> List[List[Path]]:
    if bool(group_size) == bool(groups_arg):
        raise ValueError("Specify exactly one of --group-size or --groups")

    if group_size:
        if group_size <= 0:
            raise ValueError("--group-size must be > 0")
        return [files[i : i + group_size] for i in range(0, len(files), group_size)]

    ranges = parse_ranges(groups_arg or "")
    grouped: List[List[Path]] = []
    for start, end in ranges:
        if start < 1 or end < start:
            raise ValueError(f"Invalid range: {start}-{end}")
        if end > len(files):
            raise ValueError(f"Range out of bounds: {start}-{end} for {len(files)} files")
        grouped.append(files[start - 1 : end])
    return grouped


def parse_ranges(text: str) -> List[Tuple[int, int]]:
    ranges: List[Tuple[int, int]] = []
    chunks = [chunk.strip() for chunk in text.split(",") if chunk.strip()]
    if not chunks:
        raise ValueError("--groups must contain at least one range")
    for chunk in chunks:
        match = re.fullmatch(r"(\d+)-(\d+)", chunk)
        if not match:
            raise ValueError(f"Invalid group range: {chunk}")
        ranges.append((int(match.group(1)), int(match.group(2))))
    return ranges


def infer_suffix(files: List[Path], index: int, mode: str) -> str:
    if mode == "ordinal":
        return str(index)

    start = extract_first_number(files[0].stem)
    end = extract_last_number(files[-1].stem)
    if start is None or end is None:
        return str(index)
    if start == end:
        return str(start)
    return f"{start}-{end}"


def extract_first_number(text: str) -> Optional[int]:
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def extract_last_number(text: str) -> Optional[int]:
    numbers = re.findall(r"\d+", text)
    return int(numbers[-1]) if numbers else None


def demote_headings_outside_fences(content: str) -> str:
    lines = content.splitlines(keepends=True)
    result: List[str] = []
    in_fence = False

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            result.append(line)
            continue

        if not in_fence:
            match = re.match(r"^(#{1,6})(\s+[^\n]*)(\n?)$", line)
            if match:
                hashes, tail, newline = match.groups()
                new_level = min(len(hashes) + 1, 6)
                result.append("#" * new_level + tail + newline)
                continue

        result.append(line)

    return "".join(result)


def load_file_body(path: Path, input_format: str, json_text_key: Optional[str]) -> str:
    if input_format == "md":
        original = path.read_text(encoding="utf-8")
        return demote_headings_outside_fences(original).strip()

    if input_format == "txt":
        return path.read_text(encoding="utf-8").strip()

    if json_text_key is None:
        raise ValueError("--json-text-key is required when --input-format=json")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object in {path}")
    if json_text_key not in payload:
        raise ValueError(f"Missing JSON text key '{json_text_key}' in {path}")

    text = payload[json_text_key]
    if not isinstance(text, str):
        raise ValueError(f"JSON text key '{json_text_key}' must be a string in {path}")
    return text.strip()


def build_output_body(
    prefix: str,
    suffix: str,
    files: Sequence[Path],
    input_format: str,
    json_text_key: Optional[str],
) -> str:
    heading = f"# {prefix}_{suffix}\n"
    blocks: List[str] = []
    for path in files:
        blocks.append(load_file_body(path, input_format, json_text_key))
    body = "\n\n".join(blocks)
    return heading + "\n" + body + "\n"


def create_plan(
    groups: Sequence[Sequence[Path]], out_dir: Path, prefix: str, name_mode: str
) -> List[GroupPlan]:
    plan: List[GroupPlan] = []
    used_names = set()

    for idx, files in enumerate(groups, start=1):
        suffix = infer_suffix(list(files), idx, name_mode)
        output_path = out_dir / f"{prefix}_{suffix}.md"
        if output_path.name in used_names:
            raise ValueError(f"Duplicate output filename would be created: {output_path.name}")
        used_names.add(output_path.name)
        plan.append(GroupPlan(index=idx, files=list(files), suffix=suffix, output_path=output_path))

    return plan


def print_plan(plan: Sequence[GroupPlan], dry_run: bool) -> None:
    print(f"dry_run: {dry_run}")
    print(f"groups: {len(plan)}")
    for item in plan:
        print(f"- [{item.index}] {item.output_path}")
        for source in item.files:
            print(f"  - {source}")


def write_outputs(
    plan: Sequence[GroupPlan],
    prefix: str,
    dry_run: bool,
    input_format: str,
    json_text_key: Optional[str],
) -> None:
    if dry_run:
        return
    rendered_outputs = {
        item.output_path: build_output_body(prefix, item.suffix, item.files, input_format, json_text_key)
        for item in plan
    }
    for item in plan:
        item.output_path.parent.mkdir(parents=True, exist_ok=True)
        item.output_path.write_text(rendered_outputs[item.output_path], encoding="utf-8")


def main() -> int:
    args = parse_args()
    in_dir = Path(args.in_dir)
    out_dir = Path(args.out_dir)

    try:
        validate_args(args)
        prefix = normalize_prefix(args.prefix)
        files = load_input_files(in_dir, args.input_format)
        grouped = build_groups(files, args.group_size, args.groups)
        plan = create_plan(grouped, out_dir, prefix, args.name_mode)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print_plan(plan, args.dry_run)

    try:
        write_outputs(plan, prefix, args.dry_run, args.input_format, args.json_text_key)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # noqa: BLE001
        print(f"Error: failed to write outputs: {exc}", file=sys.stderr)
        return 2

    if not args.dry_run:
        print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

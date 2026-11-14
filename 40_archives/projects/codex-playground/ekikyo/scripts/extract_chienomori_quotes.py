from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SECTION_RE = re.compile(r"^(##|###|####)\s+(.+)$")
FILE_PATTERNS = (re.compile(r"^(\d{2})\.(.+)\.md$"), re.compile(r"^(\d{2})_(.+)\.md$"))
HONKA_SECTION_NAMES = ("卦辞", "彖伝", "大象伝")
LINE_SECTION_NAMES = {
    "初九",
    "九二",
    "九三",
    "九四",
    "九五",
    "上九",
    "初六",
    "六二",
    "六三",
    "六四",
    "六五",
    "上六",
    "用九",
    "用六",
}


@dataclass(frozen=True)
class Heading:
    line_index: int
    level: str
    title: str


@dataclass(frozen=True)
class HexagramDocument:
    number: int
    name: str
    lines: list[str]
    headings: list[Heading]


class ExtractionError(Exception):
    pass


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract honka/koji classical quote pairs from Chienomori markdown files.")
    parser.add_argument(
        "--source-dir",
        default="/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/180_易経_Clip編集/183_知恵の森",
        help="Directory containing the Chienomori markdown files.",
    )
    parser.add_argument(
        "--honka-output",
        default="/home/ys/projects/ekikyo/work/chienomori-honka-taisho.md",
        help="Output path for extracted honka sections.",
    )
    parser.add_argument(
        "--koji-output",
        default="/home/ys/projects/ekikyo/work/chienomori-koji-sho.md",
        help="Output path for extracted koji sections.",
    )
    parser.add_argument(
        "--combined-output",
        default="/home/ys/projects/ekikyo/work/chienomori-honka-koji.md",
        help="Output path for combined honka/koji sections.",
    )
    return parser.parse_args(argv)


def _parse_file_number(path: Path) -> int:
    for pattern in FILE_PATTERNS:
        match = pattern.match(path.name)
        if match:
            return int(match.group(1))
    raise ExtractionError(f"unsupported source filename: {path.name}")


def _extract_frontmatter_title(text: str, path: Path) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ExtractionError(f"frontmatter not found: {path}")
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("title:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    raise ExtractionError(f"title not found in frontmatter: {path}")


def _body_start_index(lines: list[str]) -> int:
    if not lines or lines[0].strip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return index + 1
    return 0


def _extract_headings(lines: list[str], path: Path) -> list[Heading]:
    headings: list[Heading] = []
    start = _body_start_index(lines)
    for index in range(start, len(lines)):
        match = SECTION_RE.match(lines[index])
        if match:
            headings.append(Heading(line_index=index, level=match.group(1), title=match.group(2).strip()))
    if not headings:
        raise ExtractionError(f"no headings found in source body: {path}")
    return headings


def load_documents(source_dir: Path) -> list[HexagramDocument]:
    if not source_dir.is_dir():
        raise ExtractionError(f"source directory not found: {source_dir}")
    documents: list[HexagramDocument] = []
    for path in sorted(source_dir.glob("*.md"), key=_parse_file_number):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        documents.append(
            HexagramDocument(
                number=_parse_file_number(path),
                name=_extract_frontmatter_title(text, path),
                lines=lines,
                headings=_extract_headings(lines, path),
            )
        )
    if len(documents) != 64:
        raise ExtractionError(f"expected 64 source files, found {len(documents)} in {source_dir}")
    return documents


def _section_body(doc: HexagramDocument, heading_index: int) -> list[str]:
    start = doc.headings[heading_index].line_index + 1
    end = doc.headings[heading_index + 1].line_index if heading_index + 1 < len(doc.headings) else len(doc.lines)
    return doc.lines[start:end]


def _quote_pair_from_body(body: list[str], label: str, doc: HexagramDocument) -> list[str]:
    quote_lines = [line for line in body if line.startswith("> ")]
    if len(quote_lines) < 2:
        raise ExtractionError(f"{doc.number:02d} {doc.name} / {label}: quote pair not found")
    return quote_lines[:2]


def _find_heading_index(doc: HexagramDocument, *, level: str, title: str, start: int = 0) -> int:
    for index in range(start, len(doc.headings)):
        heading = doc.headings[index]
        if heading.level == level and heading.title == title:
            return index
    raise ExtractionError(f"{doc.number:02d} {doc.name}: heading not found: {level} {title}")


def _find_yao_heading_indexes(doc: HexagramDocument) -> list[int]:
    yao_root_index = _find_heading_index(doc, level="##", title="爻辞")
    indexes: list[int] = []
    for index in range(yao_root_index + 1, len(doc.headings)):
        heading = doc.headings[index]
        if heading.level == "##":
            break
        if heading.level == "###" and heading.title in LINE_SECTION_NAMES:
            indexes.append(index)
    if not indexes:
        raise ExtractionError(f"{doc.number:02d} {doc.name}: no yao headings found under 爻辞")
    return indexes


def build_honka_output(documents: list[HexagramDocument]) -> str:
    output_lines: list[str] = []
    for doc in documents:
        output_lines.append(f"## {doc.number} {doc.name}")
        output_lines.append("")
        for section_name in HONKA_SECTION_NAMES:
            heading_index = _find_heading_index(doc, level="##", title=section_name)
            output_lines.append(f"### {section_name}")
            output_lines.append("")
            output_lines.extend(_quote_pair_from_body(_section_body(doc, heading_index), section_name, doc))
            output_lines.append("")
        if output_lines[-1] == "":
            output_lines.pop()
        output_lines.append("")
    if output_lines[-1] == "":
        output_lines.pop()
    return "\n".join(output_lines) + "\n"


def build_koji_output(documents: list[HexagramDocument]) -> str:
    output_lines: list[str] = []
    for doc in documents:
        output_lines.append(f"## {doc.number} {doc.name}")
        output_lines.append("")
        for yao_index in _find_yao_heading_indexes(doc):
            yao_heading = doc.headings[yao_index]
            output_lines.append(f"### {yao_heading.title}")
            output_lines.append("")
            output_lines.extend(_quote_pair_from_body(_section_body(doc, yao_index), yao_heading.title, doc))
            output_lines.append("")
            xiaoxiang_index = _find_heading_index(doc, level="####", title="小象伝", start=yao_index + 1)
            next_line_index = None
            for candidate in range(yao_index + 1, len(doc.headings)):
                heading = doc.headings[candidate]
                if heading.level == "###" and heading.title in LINE_SECTION_NAMES:
                    next_line_index = candidate
                    break
                if heading.level == "##":
                    break
            if next_line_index is not None and xiaoxiang_index > next_line_index:
                raise ExtractionError(f"{doc.number:02d} {doc.name} / {yao_heading.title}: 小象伝 not found before next yao")
            output_lines.append("#### 小象伝")
            output_lines.append("")
            output_lines.extend(_quote_pair_from_body(_section_body(doc, xiaoxiang_index), f"{yao_heading.title} 小象伝", doc))
            output_lines.append("")
        if output_lines[-1] == "":
            output_lines.pop()
        output_lines.append("")
    if output_lines[-1] == "":
        output_lines.pop()
    return "\n".join(output_lines) + "\n"


def build_combined_output(documents: list[HexagramDocument]) -> str:
    output_lines: list[str] = []
    for doc in documents:
        output_lines.append(f"## {doc.number} {doc.name}")
        output_lines.append("")
        output_lines.append("### 本卦")
        output_lines.append("")
        for section_name in HONKA_SECTION_NAMES:
            heading_index = _find_heading_index(doc, level="##", title=section_name)
            output_lines.append(f"#### {section_name}")
            output_lines.append("")
            output_lines.extend(_quote_pair_from_body(_section_body(doc, heading_index), section_name, doc))
            output_lines.append("")
        output_lines.append("### 爻辞")
        output_lines.append("")
        for yao_index in _find_yao_heading_indexes(doc):
            yao_heading = doc.headings[yao_index]
            output_lines.append(f"#### {yao_heading.title}")
            output_lines.append("")
            output_lines.extend(_quote_pair_from_body(_section_body(doc, yao_index), yao_heading.title, doc))
            output_lines.append("")
            xiaoxiang_index = _find_heading_index(doc, level="####", title="小象伝", start=yao_index + 1)
            next_line_index = None
            for candidate in range(yao_index + 1, len(doc.headings)):
                heading = doc.headings[candidate]
                if heading.level == "###" and heading.title in LINE_SECTION_NAMES:
                    next_line_index = candidate
                    break
                if heading.level == "##":
                    break
            if next_line_index is not None and xiaoxiang_index > next_line_index:
                raise ExtractionError(f"{doc.number:02d} {doc.name} / {yao_heading.title}: 小象伝 not found before next yao")
            output_lines.append("##### 小象伝")
            output_lines.append("")
            output_lines.extend(_quote_pair_from_body(_section_body(doc, xiaoxiang_index), f"{yao_heading.title} 小象伝", doc))
            output_lines.append("")
        if output_lines[-1] == "":
            output_lines.pop()
        output_lines.append("")
    if output_lines[-1] == "":
        output_lines.pop()
    return "\n".join(output_lines) + "\n"


def write_outputs(documents: list[HexagramDocument], honka_output: Path, koji_output: Path, combined_output: Path) -> None:
    honka_output.parent.mkdir(parents=True, exist_ok=True)
    koji_output.parent.mkdir(parents=True, exist_ok=True)
    combined_output.parent.mkdir(parents=True, exist_ok=True)
    honka_output.write_text(build_honka_output(documents), encoding="utf-8")
    koji_output.write_text(build_koji_output(documents), encoding="utf-8")
    combined_output.write_text(build_combined_output(documents), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        documents = load_documents(Path(args.source_dir))
        write_outputs(documents, Path(args.honka_output), Path(args.koji_output), Path(args.combined_output))
    except ExtractionError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WORK_SECTION_HEADINGS = {
    "kaji": "## 卦辞（彖辞）",
    "tanden": ("## 彖伝", "## 彖伝（彖辞の解説）"),
    "taisho": ("## 大象伝", "## 大象伝（卦全体の解説）"),
    "lines": "## 爻辞（象辞）と象伝（小象伝）",
}


class SyncError(RuntimeError):
    pass


def _split_frontmatter(text: str) -> tuple[str, str]:
    match = re.match(r"(?s)\A(---\n.*?\n---\n)(.*)\Z", text)
    if match is None:
        raise SyncError("expected yaml frontmatter with opening and closing --- lines")
    frontmatter = match.group(1)
    body = match.group(2).lstrip("\n")
    return frontmatter, body


def _parse_frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", frontmatter, re.M)
    if match is None:
        raise SyncError(f"missing frontmatter key: {key}")
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value


def _find_heading(lines: list[str], heading: str) -> int:
    for index, line in enumerate(lines):
        if line.strip() == heading:
            return index
    raise SyncError(f"missing section heading: {heading}")


def _find_any_heading(lines: list[str], headings: tuple[str, ...] | str, start_index: int = 0) -> tuple[int, str]:
    if isinstance(headings, str):
        headings = (headings,)
    for index in range(start_index, len(lines)):
        stripped = lines[index].strip()
        if stripped in headings:
            return index, stripped
    raise SyncError(f"missing section heading: {headings[0]}")


def _extract_work_sections(body: str) -> dict[str, str]:
    lines = body.splitlines()
    kaji_index, _ = _find_any_heading(lines, WORK_SECTION_HEADINGS["kaji"])
    tanden_index, _ = _find_any_heading(lines, WORK_SECTION_HEADINGS["tanden"], kaji_index + 1)
    taisho_index, _ = _find_any_heading(lines, WORK_SECTION_HEADINGS["taisho"], tanden_index + 1)
    lines_index, _ = _find_any_heading(lines, WORK_SECTION_HEADINGS["lines"], taisho_index + 1)
    return {
        "kaji": "\n".join(lines[kaji_index + 1:tanden_index]).strip("\n"),
        "tanden": "\n".join(lines[tanden_index + 1:taisho_index]).strip("\n"),
        "taisho": "\n".join(lines[taisho_index + 1:lines_index]).strip("\n"),
        "lines": "\n".join(lines[lines_index + 1:]).strip("\n"),
    }


def _convert_line_section(text: str) -> str:
    return re.sub(r"(?m)^### ", "#### ", text).strip("\n")


def _build_body(number: str, title: str, yomi: str, work_body: str) -> str:
    sections = _extract_work_sections(work_body)
    line_section = _convert_line_section(sections["lines"])
    parts = [
        f"## {number} {title}",
        "",
        f'number: "{number}"',
        f'title: "{title}"',
        f'yomi: "{yomi}"',
        "",
        "### 本卦解釈",
        "",
        "#### 卦辞",
        "",
        sections["kaji"].strip("\n"),
        "",
        "#### 彖伝",
        "",
        sections["tanden"].strip("\n"),
        "",
        "#### 大象伝",
        "",
        sections["taisho"].strip("\n"),
        "",
        "### 変爻解釈",
        "",
        line_section,
    ]
    return "\n".join(parts).rstrip() + "\n"


def sync_one(work_path: Path, assets_path: Path, *, check: bool = False) -> bool:
    work_frontmatter, work_body = _split_frontmatter(work_path.read_text(encoding="utf-8"))
    assets_frontmatter, _ = _split_frontmatter(assets_path.read_text(encoding="utf-8"))
    number = _parse_frontmatter_value(work_frontmatter, "number")
    title = _parse_frontmatter_value(work_frontmatter, "title")
    yomi = _parse_frontmatter_value(work_frontmatter, "yomi")
    new_text = assets_frontmatter + _build_body(number, title, yomi, work_body)
    current_text = assets_path.read_text(encoding="utf-8")
    if current_text == new_text:
        return False
    if check:
        return True
    assets_path.write_text(new_text, encoding="utf-8")
    return True


def sync_all(work_dir: Path, assets_dir: Path, *, check: bool = False) -> list[Path]:
    changed: list[Path] = []
    for work_path in sorted(work_dir.glob("*.md")):
        assets_path = assets_dir / work_path.name
        if not assets_path.is_file():
            raise SyncError(f"missing assets counterpart: {assets_path}")
        if sync_one(work_path, assets_path, check=check):
            changed.append(assets_path)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync takashima assets from the work source files.")
    parser.add_argument("--work-dir", default="work/143_高島易断_増補", help="Source work directory.")
    parser.add_argument("--assets-dir", default="assets/takashima", help="Target assets directory.")
    parser.add_argument("--check", action="store_true", help="Report whether changes would be made.")
    args = parser.parse_args(argv)

    work_dir = Path(args.work_dir)
    assets_dir = Path(args.assets_dir)
    try:
        changed = sync_all(work_dir, assets_dir, check=args.check)
    except SyncError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.check:
        if changed:
            for path in changed:
                print(path)
            return 1
        return 0

    for path in changed:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

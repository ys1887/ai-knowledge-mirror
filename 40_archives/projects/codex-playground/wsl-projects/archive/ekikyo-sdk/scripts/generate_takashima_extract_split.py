from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "takashima"
OUTPUT_DIR = ROOT / "assets" / "extract_takashima_split"

TARGET_FILES = [path.name for path in sorted(SOURCE_DIR.glob("[0-6][0-9]_*.md")) if int(path.name[:2]) <= 64]

SECTION_TITLES = {
    "卦辞": "卦辞（彖辞）",
    "彖伝": "彖伝",
    "大象伝": "大象伝",
    "爻辞": "爻辞（象辞）と象伝（小象伝）",
}

SECTION_FILES = {
    "キーワード": ("keywords", "keywords.md"),
    "卦辞": ("kaji", "kaji.md"),
    "彖伝": ("tanden", "tanden.md"),
    "大象伝": ("taisho", "taisho.md"),
    "文言伝": ("bungen", "bungen.md"),
}

YAO_LABELS = {
    "初爻": (1, "初爻"),
    "2爻": (2, "二爻"),
    "3爻": (3, "三爻"),
    "4爻": (4, "四爻"),
    "5爻": (5, "五爻"),
    "上爻": (6, "上爻"),
}

SPECIAL_LABELS = {
    "用九": ("yongjiu", "yongjiu.md", "用九"),
    "用六": ("yongliu", "yongliu.md", "用六"),
}

EXCEPTIONS = [
    {
        "number": 30,
        "name": "離為火",
        "section": "五爻",
        "issue": "元 source の五爻見出しが `#### 3爻（九三）` と誤記されており、generator 側で五爻ブロックへ再結合して吸収している。",
        "status": "source_artifact_absorbed",
        "affected_files": [
            "30_離為火/yao_5.md",
        ],
    }
]


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    match = re.search(r"(?s)^---\n(.*?)\n---\n(.*)\Z", text, re.MULTILINE)
    if not match:
        raise ValueError("frontmatter not found")
    meta_lines = match.group(1).splitlines()
    body = match.group(2).lstrip("\n")
    meta = {}
    for line in meta_lines:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip().strip('"')
    return meta, body


def split_sections(body: str, level: int) -> dict[str, str]:
    marker = "#" * level
    pattern = re.compile(rf"(?m)^{re.escape(marker)} (.+?)\n")
    matches = list(pattern.finditer(body))
    sections = {}
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()
    return sections


def split_ordered_sections(body: str, level: int) -> list[tuple[str, str]]:
    marker = "#" * level
    pattern = re.compile(rf"(?m)^{re.escape(marker)} (.+?)\n")
    matches = list(pattern.finditer(body))
    sections = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        sections.append((title, body[start:end].strip()))
    return sections


def normalize_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.strip())


def yaml_value(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    escaped = value.replace('"', '\\"')
    return f'"{escaped}"'


def render_frontmatter(data: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in data.items():
        lines.append(f"{key}: {yaml_value(value)}")
    lines.append("---")
    return "\n".join(lines)


def write_markdown(path: Path, frontmatter: dict[str, object], body: str) -> None:
    content = render_frontmatter(frontmatter) + "\n\n" + body.strip() + "\n"
    path.write_text(content, encoding="utf-8")


def render_section_markdown(title: str, body: str) -> str:
    return f"### {title}\n\n{body.strip()}"


def normalize_section_key(title: str) -> str:
    if title.startswith("卦辞"):
        return "卦辞"
    if title.startswith("彖伝"):
        return "彖伝"
    if title.startswith("大象伝"):
        return "大象伝"
    if title.startswith("文言伝"):
        return "文言伝"
    if title.startswith("爻辞"):
        return "爻辞"
    return title


def normalize_yao_key(title: str) -> str:
    for key in (*YAO_LABELS.keys(), *SPECIAL_LABELS.keys()):
        if title.startswith(key):
            return key
    return title


def split_keywords(body: str) -> tuple[str, str]:
    match = re.search(r"(?m)^### ", body)
    if not match:
        return body.strip(), ""
    keywords = body[: match.start()].strip()
    rest = body[match.start() :].strip()
    return keywords, rest


def quote_block(*lines: str) -> list[str]:
    return [f"> {line}" for line in lines if line]


def looks_like_yao_block(block: str) -> bool:
    lines = [line.rstrip() for line in block.splitlines()]
    lines = [line for line in lines if line.strip()]
    if len(lines) < 4:
        return False
    if lines[1] == "**読み下し**" and len(lines) >= 5 and lines[3] == "**読み下し**":
        return True
    if len(lines) >= 6 and lines[2] == "**読み下し**" and lines[4] == "**読み下し**":
        return True
    return False


def merge_spurious_yao_entries(entries: list[tuple[str, str]]) -> list[tuple[str, str]]:
    merged: list[tuple[str, str]] = []
    for title, content in entries:
        normalized = normalize_yao_key(title)
        if normalized in SPECIAL_LABELS:
            merged.append((title, content))
            continue
        if merged and not looks_like_yao_block(content):
            prev_title, prev_content = merged[-1]
            merged[-1] = (prev_title, normalize_blank_lines(f"{prev_content}\n\n{content}"))
            continue
        merged.append((title, content))
    return merged


def parse_yao_block(block: str) -> tuple[list[str], list[str], str]:
    lines = [line.rstrip() for line in block.splitlines()]
    lines = [line for line in lines if line.strip()]
    if len(lines) < 5:
        raise ValueError(f"unexpected yao block shape: {lines[:6]}")
    ciyao_original = lines[0]
    if len(lines) >= 6 and lines[1] != "**読み下し**":
        xiaoxiang_original = lines[1]
        if lines[2] != "**読み下し**" or lines[4] != "**読み下し**":
            raise ValueError(f"unexpected reading markers: {lines[:5]}")
        ciyao_reading = lines[3]
        xiaoxiang_reading = lines[5]
        explanation = "\n".join(lines[6:]).strip()
    else:
        xiaoxiang_original = ""
        if lines[1] != "**読み下し**" or lines[3] != "**読み下し**":
            raise ValueError(f"unexpected abbreviated reading markers: {lines[:4]}")
        ciyao_reading = lines[2]
        xiaoxiang_reading = lines[4]
        explanation = "\n".join(lines[5:]).strip()
    return (
        quote_block(ciyao_original, ciyao_reading),
        quote_block(xiaoxiang_original, xiaoxiang_reading),
        explanation,
    )


def render_yao_markdown(display_label: str, ciyao_lines: list[str], xiaoxiang_lines: list[str], explanation: str) -> str:
    parts = [f"#### {display_label}", "", "**爻辞**", "", "\n".join(ciyao_lines).strip()]
    if xiaoxiang_lines:
        parts.extend(["", "**小象伝**", "", "\n".join(xiaoxiang_lines).strip()])
    if explanation:
        parts.extend(["", "**解釈**", "", explanation])
    return normalize_blank_lines("\n".join(parts))


def render_special_markdown(title: str, block: str) -> str:
    return f"### {title}\n\n{block.strip()}"


def exception_lookup(number: int) -> list[dict[str, object]]:
    return [entry for entry in EXCEPTIONS if entry["number"] == number]


def generate_hexagram(source_name: str) -> dict[str, object]:
    source_path = SOURCE_DIR / source_name
    raw = source_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    keywords_body, section_body = split_keywords(body)
    sections = {
        normalize_section_key(title): content
        for title, content in split_sections(section_body, 3).items()
    }

    folder_name = source_path.stem
    output_dir = OUTPUT_DIR / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    number = int(meta["number"])
    name = meta["title"]
    yomi = meta["yomi"]
    source_file = f"takashima_zouho/{source_name}"

    manifest_sections: dict[str, str] = {}

    write_markdown(
        output_dir / "keywords.md",
        {
            "number": number,
            "name": name,
            "section": "キーワード",
            "source": "takashima_zouho",
            "source_file": source_file,
        },
        render_section_markdown("キーワード", keywords_body),
    )
    manifest_sections["keywords"] = "keywords.md"

    for section_name in ("卦辞", "彖伝", "大象伝"):
        key, file_name = SECTION_FILES[section_name]
        write_markdown(
            output_dir / file_name,
            {
                "number": number,
                "name": name,
                "section": section_name,
                "source": "takashima_zouho",
                "source_file": source_file,
            },
            render_section_markdown(SECTION_TITLES[section_name], sections[section_name]),
        )
        manifest_sections[key] = file_name

    if "文言伝" in sections:
        key, file_name = SECTION_FILES["文言伝"]
        write_markdown(
            output_dir / file_name,
            {
                "number": number,
                "name": name,
                "section": "文言伝",
                "source": "takashima_zouho",
                "source_file": source_file,
            },
            render_section_markdown("文言伝", sections["文言伝"]),
        )
        manifest_sections[key] = file_name

    yao_entries = merge_spurious_yao_entries(split_ordered_sections(sections["爻辞"], 4))
    for index, (source_label, (yao_number, display_label)) in enumerate(YAO_LABELS.items()):
        _source_title, block = yao_entries[index]
        ciyao_lines, xiaoxiang_lines, explanation = parse_yao_block(block)
        file_name = f"yao_{yao_number}.md"
        write_markdown(
            output_dir / file_name,
            {
                "number": number,
                "name": name,
                "section": display_label,
                "yao": yao_number,
                "yao_label": display_label,
                "has_xiaoxiang": bool(xiaoxiang_lines),
                "source": "takashima_zouho",
                "source_file": source_file,
            },
            render_yao_markdown(display_label, ciyao_lines, xiaoxiang_lines, explanation),
        )
        manifest_sections[f"yao_{yao_number}"] = file_name

    extra_entries = yao_entries[len(YAO_LABELS) :]
    special_blocks = {normalize_yao_key(title): content for title, content in extra_entries}
    for source_label, (key, file_name, display_label) in SPECIAL_LABELS.items():
        if source_label not in special_blocks:
            continue
        write_markdown(
            output_dir / file_name,
            {
                "number": number,
                "name": name,
                "section": display_label,
                "source": "takashima_zouho",
                "source_file": source_file,
            },
            render_special_markdown(display_label, special_blocks[source_label]),
        )
        manifest_sections[key] = file_name

    manifest = {
        "number": number,
        "name": name,
        "yomi": yomi,
        "source": "takashima_zouho",
        "source_file": source_file,
        "sections": manifest_sections,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    hexagram_exceptions = exception_lookup(number)
    return {
        "number": number,
        "name": name,
        "folder_path": f"assets/extract_takashima_split/{folder_name}",
        "sections": list(manifest_sections.keys()),
        "special_sections": {
            "bungen": False,
            "yongjiu": "yongjiu" in manifest_sections,
            "yongliu": "yongliu" in manifest_sections,
        },
        "has_exceptions": bool(hexagram_exceptions),
    }


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    index = [generate_hexagram(source_name) for source_name in TARGET_FILES]
    (OUTPUT_DIR / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUTPUT_DIR / "exceptions.json").write_text(
        json.dumps(EXCEPTIONS, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

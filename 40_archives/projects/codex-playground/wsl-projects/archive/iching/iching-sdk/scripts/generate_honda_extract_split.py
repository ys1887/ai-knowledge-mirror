from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "sources" / "extract" / "honda_wataru"
OUTPUT_DIR = ROOT / "sources" / "extract_honda_split"

TARGET_FILES = [path.name for path in sorted(SOURCE_DIR.glob("[0-6][0-9]_*.md")) if int(path.name[:2]) <= 64]

SECTION_FILES = {
    "キーワード": ("keywords", "keywords.md"),
    "序卦伝": ("jokaden", "jokaden.md"),
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

MANUAL_XIAOXIANG_01 = {
    1: [
        "> 潛龍勿用、陽在下也。",
        "> 潜龍用うるなかれとは、陽にして 下 しも に在ればなり。",
    ],
    2: [
        "> 見龍在田、徳施普也。",
        "> 見龍 田 でん に在りとは、徳の施し 普 あまね きなり。",
    ],
    3: [
        "> 終日乾乾、反復道也。",
        "> 終日乾乾すとは、道を反復するなり。",
    ],
    4: [
        "> 或躍在淵、進无咎也。",
        "> あるいは躍りて淵に在りとは、進むも咎なきなり。",
    ],
    5: [
        "> 飛龍在天、大人造也。",
        "> 飛龍天に在りとは、大人の造なるなり。",
    ],
    6: [
        "> 亢龍有悔、盈不可久也。",
        "> 亢龍悔ありとは、盈つれば久しかるべからざるなり。",
    ],
}

EXCEPTIONS = [
    {
        "number": 1,
        "name": "乾為天",
        "section": "大象伝 / 各爻",
        "issue": "小象伝の原文と解説が大象伝に一括収録されており、各爻 inline では分離されていない。",
        "status": "partial",
        "affected_files": [
            "01_乾為天/taisho.md",
            "01_乾為天/yao_1.md",
            "01_乾為天/yao_2.md",
            "01_乾為天/yao_3.md",
            "01_乾為天/yao_4.md",
            "01_乾為天/yao_5.md",
            "01_乾為天/yao_6.md",
        ],
    },
    {
        "number": 1,
        "name": "乾為天",
        "section": "各爻",
        "issue": "各爻の小象伝引用は大象伝の集約ブロックから転記し、解説本文は帰属曖昧なため taisho.md 側に残置した。",
        "status": "partial",
        "affected_files": [
            "01_乾為天/taisho.md",
            "01_乾為天/yao_1.md",
            "01_乾為天/yao_2.md",
            "01_乾為天/yao_3.md",
            "01_乾為天/yao_4.md",
            "01_乾為天/yao_5.md",
            "01_乾為天/yao_6.md",
        ],
    },
    {
        "number": 51,
        "name": "震為雷",
        "section": "五爻",
        "issue": "元 source の五爻引用末尾に余分な `**` が含まれており、そのまま split 出力へ残る。",
        "status": "source_artifact",
        "affected_files": [
            "51_震為雷/yao_5.md",
        ],
    },
    {
        "number": 54,
        "name": "雷澤帰妹",
        "section": "上爻",
        "issue": "元 source の上爻小象伝末尾に余分な `上` が含まれており、そのまま split 出力へ残る。",
        "status": "source_artifact",
        "affected_files": [
            "54_雷澤帰妹/yao_6.md",
        ],
    },
    {
        "number": 61,
        "name": "風澤中孚",
        "section": "大象伝",
        "issue": "元 source の大象伝引用末尾に余分な `**` が含まれており、そのまま split 出力へ残る。",
        "status": "source_artifact",
        "affected_files": [
            "61_風澤中孚/taisho.md",
        ],
    },
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


def collect_quote_and_explanation(block: str) -> tuple[list[str], str]:
    quote_lines = []
    explanation_lines = []
    for line in block.splitlines():
        if line.startswith(">"):
            quote_lines.append(line.rstrip())
        else:
            explanation_lines.append(line.rstrip())
    explanation = "\n".join(explanation_lines).strip()
    return quote_lines, explanation


def split_quote_line(line: str, marker: str) -> tuple[str, str]:
    text = line[1:].lstrip()
    before, after = text.split(marker, 1)
    return f"> {before.strip()}", f"> {marker}{after}"


def split_inline_xiaoxiang(quote_lines: list[str]) -> tuple[list[str], list[str]]:
    ciyao = []
    xiaoxiang = []
    for line in quote_lines:
        if " 象曰" in line:
            before, after = split_quote_line(line, "象曰")
            ciyao.append(before)
            xiaoxiang.append(after)
        elif " 象に曰く" in line:
            before, after = split_quote_line(line, "象に曰く")
            ciyao.append(before)
            xiaoxiang.append(after)
        else:
            ciyao.append(line)
    return ciyao, xiaoxiang


def normalize_blank_lines(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    return text


def render_yao_markdown(display_label: str, ciyao_lines: list[str], xiaoxiang_lines: list[str], explanation: str) -> str:
    parts = [f"#### {display_label}", "", "**爻辞**", "", "\n".join(ciyao_lines).strip()]
    if xiaoxiang_lines:
        parts.extend(["", "**小象伝**", "", "\n".join(xiaoxiang_lines).strip()])
    if explanation:
        parts.extend(["", "**解釈**", "", explanation.strip()])
    return normalize_blank_lines("\n".join(parts))


def render_special_markdown(title: str, block: str) -> str:
    return f"### {title}\n\n{block.strip()}"


def exception_lookup(number: int) -> list[dict[str, object]]:
    return [entry for entry in EXCEPTIONS if entry["number"] == number]


def generate_hexagram(source_name: str) -> dict[str, object]:
    source_path = SOURCE_DIR / source_name
    raw = source_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    sections = split_sections(body, 3)

    folder_name = source_path.stem
    output_dir = OUTPUT_DIR / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    number = int(meta["number"])
    name = meta["title"]
    yomi = meta["yomi"]
    source_file = f"honda_wataru/{source_name}"

    manifest_sections: dict[str, str] = {}

    for section_name in ("キーワード", "序卦伝", "卦辞", "彖伝", "大象伝"):
        key, file_name = SECTION_FILES[section_name]
        write_markdown(
            output_dir / file_name,
            {
                "number": number,
                "name": name,
                "section": section_name,
                "source": "honda_wataru",
                "source_file": source_file,
            },
            render_section_markdown(section_name, sections[section_name]),
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
                "source": "honda_wataru",
                "source_file": source_file,
            },
            render_section_markdown("文言伝", sections["文言伝"]),
        )
        manifest_sections[key] = file_name

    yao_blocks = split_sections(sections["爻辞"], 4)
    for source_label, (yao_number, display_label) in YAO_LABELS.items():
        block = yao_blocks[source_label]
        quote_lines, explanation = collect_quote_and_explanation(block)
        ciyao_lines, xiaoxiang_lines = split_inline_xiaoxiang(quote_lines)
        if number == 1:
            xiaoxiang_lines = MANUAL_XIAOXIANG_01[yao_number]
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
                "source": "honda_wataru",
                "source_file": source_file,
            },
            render_yao_markdown(display_label, ciyao_lines, xiaoxiang_lines, explanation),
        )
        manifest_sections[f"yao_{yao_number}"] = file_name

    for source_label, (key, file_name, display_label) in SPECIAL_LABELS.items():
        if source_label not in yao_blocks:
            continue
        write_markdown(
            output_dir / file_name,
            {
                "number": number,
                "name": name,
                "section": display_label,
                "source": "honda_wataru",
                "source_file": source_file,
            },
            render_special_markdown(display_label, yao_blocks[source_label]),
        )
        manifest_sections[key] = file_name

    manifest = {
        "number": number,
        "name": name,
        "yomi": yomi,
        "source": "honda_wataru",
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
        "folder_path": f"sources/extract_honda_split/{folder_name}",
        "sections": list(manifest_sections.keys()),
        "special_sections": {
            "bungen": "bungen" in manifest_sections,
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

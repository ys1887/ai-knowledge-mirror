#!/usr/bin/env python3
"""
表記揺れ (notation inconsistency) checker.
Compares > L1 / > L2 quote pairs by (hexagram_number, L1) across 5 sources,
then writes a markdown report to stdout.
"""

import re
import sys
import json
from pathlib import Path
from collections import defaultdict

# ── helpers ────────────────────────────────────────────────────────────────

def normalize(text: str) -> str:
    return text.rstrip()

RUBY_RE = re.compile(r'（[^）]*）')

def is_ruby_only_diff(a: str, b: str) -> bool:
    """True if a and b differ only by presence/absence of ruby annotations."""
    return RUBY_RE.sub('', a) == RUBY_RE.sub('', b)

# Line-position names that indicate an individual-line section (爻辞/小象伝)
LINE_POSITIONS = re.compile(
    r'^(初九|初六|九二|六二|九三|六三|九四|六四|九五|六五|上九|上六|用九|用六)$'
)

# ── parsers ────────────────────────────────────────────────────────────────

def parse_source_file(path: Path):
    """
    Parse 易経_2行版.md.
    Headings: ## N 卦名  (no dot, not zero-padded)
    Returns:
        pairs:    {(hex_num, l1): l2}
        sections: {(hex_num, l1): section_label}
    """
    pairs = {}
    sections = {}
    current_hex = None
    current_section = None
    pair_in_section = 0   # count pairs within a line-position section

    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')

        # Hexagram heading
        m = re.match(r'^## (\d+)\s+\S', line)
        if m:
            current_hex = int(m.group(1))
            current_section = None
            pair_in_section = 0
            i += 1
            continue

        # Sub-section heading (###)
        m = re.match(r'^### (.+)', line)
        if m:
            heading = m.group(1).strip()
            current_section = heading
            pair_in_section = 0
            i += 1
            continue

        # Quote pair
        if line.startswith('> ') and current_hex is not None:
            l1 = normalize(line[2:])
            if i + 1 < len(lines):
                next_line = lines[i + 1].rstrip('\n')
                if next_line.startswith('> '):
                    l2 = normalize(next_line[2:])
                    key = (current_hex, l1)
                    pairs[key] = l2
                    # Determine section label
                    if current_section is None:
                        sec_label = '(unknown)'
                    elif LINE_POSITIONS.match(current_section):
                        # Alternating: 1st pair = 爻辞, 2nd pair = 小象伝
                        sec_label = f'{current_section} 爻辞' if pair_in_section % 2 == 0 else f'{current_section} 小象伝'
                    else:
                        sec_label = current_section
                    sections[key] = sec_label
                    pair_in_section += 1
                    i += 2
                    continue

        i += 1

    return pairs, sections


def parse_honka_koji(path: Path):
    """
    Parse honka.md or koji.md.
    Headings: ## N 卦名  or  ## N. 卦名
    Returns: {(hex_num, l1): l2}
    """
    pairs = {}
    current_hex = None

    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')

        m = re.match(r'^## (\d+)[.\s]', line)
        if m:
            current_hex = int(m.group(1))
            i += 1
            continue

        if line.startswith('> ') and current_hex is not None:
            l1 = normalize(line[2:])
            if i + 1 < len(lines):
                next_line = lines[i + 1].rstrip('\n')
                if next_line.startswith('> '):
                    l2 = normalize(next_line[2:])
                    pairs[(current_hex, l1)] = l2
                    i += 2
                    continue

        i += 1

    return pairs


def parse_single_file(path: Path, hex_num: int):
    """Parse one 141/143 file; returns {(hex_num, l1): l2}."""
    pairs = {}

    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')

        if line.startswith('> '):
            l1 = normalize(line[2:])
            if i + 1 < len(lines):
                next_line = lines[i + 1].rstrip('\n')
                if next_line.startswith('> '):
                    l2 = normalize(next_line[2:])
                    pairs[(hex_num, l1)] = l2
                    i += 2
                    continue

        i += 1

    return pairs


def parse_numbered_dir(dir_path: Path):
    """Parse all NN_*.md files in a directory; returns {(hex_num, l1): l2}."""
    pairs = {}
    for md_file in sorted(dir_path.glob('*.md')):
        m = re.match(r'^(\d+)_', md_file.name)
        if m:
            hex_num = int(m.group(1))
            pairs.update(parse_single_file(md_file, hex_num))
    return pairs


# ── known structural issues ────────────────────────────────────────────────

KNOWN_ISSUES = {
    # (hex_num, partial_l1_fragment): description
    (34, '彖曰'): 'hex 34 彖伝 split known',
    (38, '彖曰'): 'hex 38 彖伝 split known',
    (15, '謙'): 'hex 15 extra pairs in koji.md known',
    (28, '大過'): 'hex 28 extra pairs in koji.md known',
}

def is_known(hex_num: int, l1: str) -> str | None:
    for (h, frag), desc in KNOWN_ISSUES.items():
        if h == hex_num and frag in l1:
            return desc
    return None


# ── main ───────────────────────────────────────────────────────────────────

def main():
    BASE = Path('/home/ys/projects/ekikyo')
    SOURCE_PATH  = Path('/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/易経_2行版.md')
    HONKA_PATH   = BASE / 'assets/honka.md'
    KOJI_PATH    = BASE / 'assets/koji.md'
    DIR_141      = Path('/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/140_高島易断/141_高島易断')
    DIR_143      = Path('/mnt/c/Users/nekol/Proton Drive/Obsidian/100_易経/140_高島易断/143_高島易断_増補')

    eprint = lambda msg: print(msg, file=sys.stderr)

    eprint("Parsing source (易経_2行版.md)…")
    source_pairs, source_sections = parse_source_file(SOURCE_PATH)
    eprint(f"  {len(source_pairs)} pairs")

    eprint("Parsing honka.md…")
    honka = parse_honka_koji(HONKA_PATH)
    eprint(f"  {len(honka)} pairs")

    eprint("Parsing koji.md…")
    koji = parse_honka_koji(KOJI_PATH)
    eprint(f"  {len(koji)} pairs")

    eprint("Parsing 141_高島易断…")
    t141 = parse_numbered_dir(DIR_141)
    eprint(f"  {len(t141)} pairs")

    eprint("Parsing 143_高島易断_増補…")
    t143 = parse_numbered_dir(DIR_143)
    eprint(f"  {len(t143)} pairs")

    SOURCES = {
        'source (易経_2行版)': source_pairs,
        'honka.md':           honka,
        'koji.md':            koji,
        '141_高島易断':        t141,
        '143_高島易断_増補':   t143,
    }

    # ── collect all (hex_num, l1) keys ──
    all_keys = set()
    for s in SOURCES.values():
        all_keys.update(s.keys())

    # ── find mismatches ──
    findings_by_hex: dict[int, list] = defaultdict(list)
    total_mismatch = 0
    ruby_only_count = 0

    for key in sorted(all_keys):
        hex_num, l1 = key

        present = {name: data[key] for name, data in SOURCES.items() if key in data}
        if len(present) < 2:
            continue

        unique_l2s = set(present.values())
        if len(unique_l2s) == 1:
            continue

        # Classify
        all_vals = list(present.values())
        ruby_only = all(is_ruby_only_diff(all_vals[0], v) for v in all_vals[1:])
        known = is_known(hex_num, l1)
        section = source_sections.get(key, '(不明)')

        total_mismatch += 1
        if ruby_only:
            ruby_only_count += 1

        findings_by_hex[hex_num].append({
            'l1': l1,
            'section': section,
            'present': present,
            'ruby_only': ruby_only,
            'known': known,
        })

    eprint(f"\nTotal mismatches: {total_mismatch}  (ruby-only: {ruby_only_count})")

    # ── load hex name map from source ──
    hex_names: dict[int, str] = {}
    with open(SOURCE_PATH, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'^## (\d+)\s+(.+)', line.rstrip('\n'))
            if m:
                hex_names[int(m.group(1))] = m.group(2).strip()

    # ── render report ──
    lines_out = []
    W = lines_out.append

    W("# 表記揺れ チェックレポート")
    W("")
    W("## 概要")
    W("")
    W("| ソース | ペア数 |")
    W("|--------|--------|")
    for name, data in SOURCES.items():
        W(f"| {name} | {len(data)} |")
    W("")
    W(f"- **総不一致数**: {total_mismatch}")
    W(f"- ルビ注記の有無のみの差異（許容範囲）: {ruby_only_count}")
    W(f"- その他の差異: {total_mismatch - ruby_only_count}")
    W("")
    W("### 凡例")
    W("- 🟡 ルビ注記の有無のみの差異（許容範囲内）")
    W("- 🔴 それ以外の表記差異（要確認）")
    W("- 🔵 既知の構造的不一致")
    W("")
    W("---")
    W("")

    if not findings_by_hex:
        W("## 結果: 差異なし")
        W("")
        W("全ての L2 が一致しました。")
    else:
        W("## 差異一覧（卦番号順）")
        W("")

        for hex_num in sorted(findings_by_hex.keys()):
            hex_name = hex_names.get(hex_num, '?')
            findings = findings_by_hex[hex_num]

            W(f"### {hex_num}. {hex_name}")
            W("")

            for f in findings:
                badge = '🔵' if f['known'] else ('🟡' if f['ruby_only'] else '🔴')
                W(f"#### {badge} [{f['section']}] `{f['l1']}`")
                W("")
                if f['known']:
                    W(f"> **既知の問題**: {f['known']}")
                    W("")
                for src_name, l2_val in sorted(f['present'].items()):
                    W(f"- **{src_name}**: `{l2_val}`")
                W("")

    W("---")
    W("")
    W("## 備考: 既知の構造的不一致")
    W("")
    W("以下の差異は過去の整合性監査で把握済みです:")
    W("")
    W("- hex 34 / 38: 彖伝の分割方法の違い")
    W("- hex 15 / 28: koji.md に余分なペアが存在")
    W("- hex 01 / 02: 143_増補 に用九・用六が含まれる")
    W("- hex 30: 143_増補 でブロッククォートの漏れ")

    print('\n'.join(lines_out))


if __name__ == '__main__':
    main()

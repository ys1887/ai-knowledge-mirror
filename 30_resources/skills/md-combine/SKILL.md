---
name: md-combine
description: 複数の Markdown / txt / json ファイルを整理して 1 つ以上の Markdown に結合する skill。
---

# MD Combine (Codex)

## Purpose
Merge multiple Markdown, text, or OCR JSON files into grouped outputs with consistent Markdown structure for AI-friendly reading.

## Use This Skill When
- You need to merge `.md`, `.txt`, or `.json` files in deterministic order.
- You want a top heading added to each merged output.
- You need heading demotion by one level outside code fences for Markdown inputs.
- You want safe, repeatable output without modifying source files.
- You want to convert page-by-page OCR outputs into one Markdown file.

## Required Behavior
- Keep source files unchanged.
- Add one top heading per output: `# <prefix>_<suffix>`.
- For `.md` input, demote body headings by one level (`#` -> `##`, `##` -> `###`, ... up to `######`).
- For `.md` input, do not transform headings inside fenced code blocks.
- For `.txt` input, use the UTF-8 text body as-is.
- For `.json` input, extract the UTF-8 text body from a root-level key specified by `--json-text-key`.
- Insert one blank line between merged source file bodies.

## Naming
- Default naming mode is `auto-range`.
- Output file name: `<prefix>_<suffix>.md`.
- In `auto-range`, suffix is inferred from source names (for example `2-5`, `1-12`).
- If range inference fails, fallback suffix is ordinal (`1`, `2`, ...).

## Script
- Main helper: `scripts/merge_md_combines.py`

## Input Options
- Default input format is `md`.
- Use `--input-format txt` for plain text OCR page outputs.
- Use `--input-format json --json-text-key <key>` for JSON OCR page outputs.
- `--json-text-key` is required for JSON mode to prioritize correctness over heuristic guessing.

## Typical Commands
```bash
python3 scripts/merge_md_combines.py --in-dir "/path/in" --out-dir "/path/out" --prefix "honda_wataru" --group-size 8
```

```bash
python3 scripts/merge_md_combines.py --in-dir "/path/in" --out-dir "/path/out" --prefix "keiji" --groups "1-3,4-6"
```

```bash
python3 scripts/merge_md_combines.py --in-dir "/path/in" --out-dir "/path/out" --prefix "preview" --group-size 8 --dry-run
```

```bash
python3 scripts/merge_md_combines.py --in-dir "/path/txt_pages" --out-dir "/path/out" --prefix "ocr_book" --input-format txt --groups "1-20"
```

```bash
python3 scripts/merge_md_combines.py --in-dir "/path/json_pages" --out-dir "/path/out" --prefix "ocr_book" --input-format json --json-text-key text --group-size 50
```

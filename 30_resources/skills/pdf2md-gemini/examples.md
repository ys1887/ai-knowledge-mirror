# PDF2MD-GEMINI Skill Examples (Codex)

## Codex request examples

```text
PDF2MD-GEMINI Request
- Input path: /mnt/e/Documents/Workspace/inbox/kokoro-pages
- Writing mode: vertical
- Model: pro
```

```text
PDF2MD-GEMINI Request
- Input path: /mnt/e/Documents/Workspace/inbox/manuals/chapter1
- Writing mode: horizontal
- Model: flash
- Output path: /mnt/e/Documents/Workspace/ocr/manuals-2026-02
```

```text
PDF2MD-GEMINI Request
- Input path: /mnt/e/Documents/Workspace/inbox/book/page001.jpg
- Writing mode: vertical
- Model: thinking
- Output path: /mnt/e/Documents/Workspace/ocr/custom/page001.md
```

## Script command examples

```bash
# Folder input (non-recursive), default output layout
python3 scripts/pdf_to_md.py --in "/mnt/e/Documents/Workspace/inbox/kokoro-pages" --writing-mode vertical --model pro

# Folder input with explicit output directory
python3 scripts/pdf_to_md.py --in "./inbox/manuals/chapter1" --writing-mode horizontal --model flash --out "./ocr/manuals-2026-02"

# Single file with explicit markdown file path
python3 scripts/pdf_to_md.py --in "./inbox/book/page001.jpg" --writing-mode vertical --model thinking --out "./ocr/custom/page001.md"

# Disable raw output
python3 scripts/pdf_to_md.py --in "./inbox/sample" --writing-mode horizontal --model flash --no-save-raw
```

# PDF2MD Skill Examples (Codex)

## Codex request examples

```text
PDF2MD Request
- Input path: /mnt/e/Documents/Workspace/inbox/book1.pdf
```

```text
PDF2MD Request
- Input path: /mnt/e/Documents/Workspace/inbox/reports
- Output path: /mnt/e/Documents/Workspace/ocr/reports-2026-02
```

```text
PDF2MD Request
- Input path: /mnt/e/Documents/Workspace/inbox/scanned.pdf
- OCR language: jpn
- OCR threshold: 20
```

## Script command examples

```bash
# Single PDF, default output layout
python3 scripts/pdf_to_md.py --in "/mnt/e/Documents/Workspace/inbox/book1.pdf"

# Folder input (non-recursive) with explicit output directory
python3 scripts/pdf_to_md.py --in "./inbox/reports" --out "./ocr/reports-2026-02"

# Force OCR fallback more aggressively (lower threshold)
python3 scripts/pdf_to_md.py --in "./inbox/scanned.pdf" --lang jpn --min-chars 20

# Disable raw output
python3 scripts/pdf_to_md.py --in "./inbox/sample.pdf" --no-save-raw
```

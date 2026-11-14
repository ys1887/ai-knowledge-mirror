# PDF2MD Skill Reference (Codex)

## Runtime

- Script: `scripts/pdf_to_md.py`
- Local dependencies: `pdftotext`, `ocrmypdf`

## CLI

```bash
python3 scripts/pdf_to_md.py --in INPUT [--out OUTPUT] [--lang LANG] [--min-chars N] [--page-separator SEP] [--no-save-raw]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--in` | Yes | - | Input PDF file or directory |
| `--out` | No | auto | Output file or directory |
| `--lang` | No | `jpn` | OCR language for `ocrmypdf` |
| `--min-chars` | No | `40` | OCR fallback threshold (non-whitespace chars) |
| `--page-separator` | No | `---` | Separator text between pages |
| `--no-save-raw` | No | raw enabled | Disable raw extracted text output |

## Supported inputs

- `.pdf`

Directory input mode:

- Non-recursive (direct children only)
- Non-PDF files are ignored

## Output resolution

When `--out` is omitted:

1. Run directory = `/mnt/e/Documents/Workspace/ocr/<auto-name>`
2. Markdown output = `<run-dir>/md/<stem>.md`
3. Raw output = `<run-dir>/raw/<stem>.raw.txt`

When `--out` is a directory:

- Markdown output = `<out>/md/<stem>.md`
- Raw output = `<out>/raw/<stem>.raw.txt`

When `--out` is a file path:

- Valid only for single-file input
- Markdown output = exactly that file path
- Raw output = `<file-parent>/raw/<file-stem>.raw.txt`

## Extraction logic

- Step 1: Try `pdftotext` extraction first.
- Step 2: If extracted non-whitespace chars are below `--min-chars`, run OCR via `ocrmypdf`.
- Step 3: Extract text again from OCR-processed PDF.
- Step 4: Save markdown and optional raw output.

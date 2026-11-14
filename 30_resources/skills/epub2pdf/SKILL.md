---
name: epub2pdf
description: EPUBファイルをPDFに変換するskill。
---

# EPUB to PDF (Codex)

## Purpose
Convert EPUB files to PDF with one reusable command.

## What this skill provides
- Single-file conversion and folder batch conversion in one script.
- Safe default behavior: existing PDFs are skipped.
- Optional overwrite mode when you need to regenerate PDFs.
- Optional recursive folder scan.
- Dry-run mode to preview targets before converting.
- Execution log file for each run.

## Dependency
- `ebook-convert` (Calibre CLI)

Preferred on Ubuntu/WSL:

```bash
sudo apt update
sudo apt install -y calibre
```

Fallback (auto-detected by script):
- Windows Calibre at `/mnt/c/Program Files/Calibre2/ebook-convert.exe`

Resolver order:
1. `ebook-convert` in WSL `PATH` (recommended)
2. Windows Calibre executable path above

## Files
- Script: `scripts/epub2pdf`
- Logs: `logs/epub2pdf-YYYYMMDD-HHMMSS.log`

## Usage
From the skill folder:

```bash
./scripts/epub2pdf --in <input>
```

From a parent working folder where `epub2pdf/` was copied:

```bash
./epub2pdf/scripts/epub2pdf --in <input>
```

## Options
- `--in <path>`: required. EPUB file or input directory.
- `--out <path>`: optional.
  - file input: PDF file path or output directory.
  - directory input: output directory.
- `--recursive`: directory mode only. Include subdirectories.
- `--overwrite`: overwrite existing PDFs.
- `--dry-run`: show actions without converting.
- `--help`: show help.

## Default behavior
- File input + no `--out`: writes `<same-dir>/<name>.pdf`.
- Directory input + no `--out`: writes to input directory.
- Existing output PDF: skip (unless `--overwrite` is set).

## Examples
Batch convert a folder:

```bash
./epub2pdf/scripts/epub2pdf --in ./books --out ./pdfs
```

Batch convert including subfolders:

```bash
./epub2pdf/scripts/epub2pdf --in ./books --out ./pdfs --recursive
```

Convert one file to a directory:

```bash
./epub2pdf/scripts/epub2pdf --in ./book.epub --out ./pdfs
```

Convert one file to a specific filename:

```bash
./epub2pdf/scripts/epub2pdf --in ./book.epub --out ./output/my-book.pdf
```

Preview only:

```bash
./epub2pdf/scripts/epub2pdf --in ./books --out ./pdfs --recursive --dry-run
```

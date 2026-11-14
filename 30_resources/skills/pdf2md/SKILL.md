---
name: pdf2md
description: PDFをローカルでMarkdownに変換するskill。
---

# PDF2MD (Codex)

## Purpose
Convert PDF files to Markdown using local tools only.
This is the default local variant for PDF -> text extraction -> Markdown save.

## Scope
- Input type: PDF only (`.pdf`)
- Automatic flow: text extraction -> OCR fallback (if needed) -> Markdown save
- No API usage

## Defaults
- Multi-page separator is `---`.
- Raw extracted text is saved unless disabled.
- Embedded PDF images are extracted and linked in Markdown by default.
- Directory input is non-recursive.

## Required Inputs
- Input path (`--in`): file or directory.

## Optional Inputs
- Output path (`--out`): file or directory.
- OCR language (`--lang`): default `jpn`.
- OCR fallback threshold (`--min-chars`): default `40` non-whitespace chars.
- Page separator (`--page-separator`): default `---`.
- Image extraction controls:
  - `--no-extract-images`
  - `--no-embed-images`
  - `--images-dir`
  - `--image-format` (current support: `png`)

## Output Behavior
- Default base output directory: `/mnt/e/Documents/Workspace/ocr`.
- A run directory is auto-created from input name.
- Markdown files are stored under `md/`.
- Raw extracted text files are stored under `raw/`.
- Extracted images are stored under `images/<input_stem>/`.

## Dependencies
- `pdftotext` (from `poppler-utils`)
- `ocrmypdf` (with `tesseract-ocr` language data)
- `pdfimages` (from `poppler-utils`) for image extraction

## Script
- `scripts/pdf_to_md.py`

## Notes
- Keep `README.md` in Japanese for user-facing operation.
- Keep SKILL docs concise and implementation-aligned.

---
name: pdf2md-gemini
description: PDFや画像をGeminiでOCRしてMarkdown化するskill。
---

# PDF2MD-GEMINI (Codex)

## Purpose
Convert Japanese documents to Markdown using Gemini OCR with strict source fidelity.
This skill is PDF-first and also supports common image formats.
This is the API-based fully automated variant.

## Defaults
- Japanese-only OCR behavior.
- Strict fidelity mode (preserve line breaks, punctuation, and paragraph order).
- Raw OCR text is always saved unless explicitly disabled.
- Page separator is `---` for multi-page documents.
- For PDF input, embedded images are extracted and linked in Markdown by default.

## Required Inputs
- Input path (`--in`): file or directory.
- Writing mode (`--writing-mode`): `vertical` or `horizontal`.
- Model profile (`--model`): `flash`, `thinking`, or `pro`.
- `GEMINI_API_KEY` must be set in the environment.

## Output Behavior
- Default base output directory: `/mnt/e/Documents/Workspace/ocr`.
- A run directory is auto-created from input name (sanitized for filesystem safety).
- Markdown files are stored under `md/`.
- Raw OCR text files are stored under `raw/`.
- Extracted images are stored under `images/<input_stem>/`.
- `--out` can override output destination with file path or directory path.

## Directory Processing
- Directory input processes only files directly under that directory.
- Subdirectories are not processed.
- Supported file types: `.jpg`, `.jpeg`, `.png`, `.webp`, `.pdf`.

## Model Mapping
- `flash` -> `PDF2MD_MODEL_FLASH` env var (fallback default in script)
- `thinking` -> `PDF2MD_MODEL_THINKING` env var (fallback default in script)
- `pro` -> `PDF2MD_MODEL_PRO` env var (fallback default in script)

## Script
- `scripts/pdf_to_md.py`

## Image Options
- `--no-extract-images`
- `--no-embed-images`
- `--images-dir`
- `--image-format` (current support: `png`)

## Notes
- Keep `README.md` in Japanese for user-facing operation.
- Keep SKILL docs concise and implementation-aligned.

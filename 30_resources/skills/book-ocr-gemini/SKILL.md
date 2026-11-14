---
name: book-ocr-gemini
description: 書籍画像やPDFをOCRして読みやすいMarkdownにまとめるskill。
---

# BOOK_OCR_GEMINI (Codex)

## Purpose
Convert book sources (image folders or single PDFs) into a single Markdown file with:
- OCR via Gemini API
- line-break restoration (keep intentional breaks, join wraps)
- optional furigana normalization like `孔穎達（くようたつ）`

## When to use
- Book/page OCR requests where plain OCR output has broken wrapping
- Multi-page image sets that should become one Markdown
- OCR runs needing readable text while preserving structure

## Required Inputs
- `--in`: image directory or a single file (`.jpg/.jpeg/.png/.webp/.heic/.heif/.pdf`)
- `--writing-mode`: `vertical` or `horizontal`
- `--model`: `flash`, `thinking`, or `pro`
- `GEMINI_API_KEY` env var

## Defaults
- `--linebreak-mode heuristic`
- `--furigana-mode none`
- `--paren-policy no-ruby`
- `--page-separator ---`
- Output is a single Markdown file (no overwrite unless `--overwrite`)

## Script
- `scripts/book_ocr_linebreak.py`

## Notes
- OCR text quality can vary across runs, especially with `flash`; use `pro` for higher stability.
- Ruby-like parenthetical noise can be filtered with `--paren-policy no-ruby` (default).
- The furigana formatter is heuristic and intentionally conservative (off by default).
- See `references/linebreak-and-furigana.md` for normalization rules.

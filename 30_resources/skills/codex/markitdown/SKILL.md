---
name: markitdown
description: Convert a local PDF, DOCX, PPTX, XLSX, HTML, EPUB, CSV, JSON, XML, text file, or similar document to Markdown by running the installed MarkItDown CLI. Use when the user asks to convert a file to Markdown, says "Markdown化して", "convert this to markdown", or wants repeated single-file conversions in one chat.
metadata:
  short-description: Convert local files to Markdown with MarkItDown CLI
---

# MarkItDown

Use the local MarkItDown CLI for file-to-Markdown conversion.

## CLI Path
- `/home/ys/tools/markitdown/.venv/bin/markitdown`

## Use This Skill When
- The user wants a local file converted to Markdown.
- The request is about PDF, DOCX, PPTX, XLSX, HTML, EPUB, CSV, JSON, XML, TXT, or similar document conversion.
- The user wants to convert one file now, then another file later in the same chat.

## Do Not Use This Skill When
- The user wants analysis, summarization, rewriting, or extraction after conversion unless they ask for that explicitly.
- The user wants directory-wide batch conversion as the main workflow.
- The input path is missing and cannot be inferred safely.

## Default Behavior
- Process one file per instruction.
- Default output path is next to the input file, using the same stem and a `.md` extension.
- Use this command shape:

```bash
/home/ys/tools/markitdown/.venv/bin/markitdown <input> -o <input_dir>/<input_stem>.md
```

## Guardrails
- If the input path is ambiguous, ask for clarification before running anything.
- If the default output file already exists and overwrite intent is unclear, ask before replacing it.
- Report CLI warnings clearly, including optional runtime warnings such as missing `ffmpeg` for audio-related features.
- Do not invent post-processing. Only convert and report the result unless the user asks for more.

## Workflow
1. Confirm the input file path.
2. Compute the default sibling output path with a `.md` extension.
3. Check whether the output path already exists.
4. If the path is safe, run MarkItDown with `-o`.
5. Report the output path and any warnings or conversion failures.

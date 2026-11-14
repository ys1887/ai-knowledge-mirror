# PDF2MD-GEMINI Skill Reference (Codex)

## Runtime

- Script: `scripts/pdf_to_md.py`
- API endpoint base: `https://generativelanguage.googleapis.com/v1beta/models`
- API key env var: `GEMINI_API_KEY`

## CLI

```bash
python3 scripts/pdf_to_md.py --in INPUT --writing-mode MODE --model PROFILE [--out OUTPUT] [--page-separator SEP] [--no-save-raw]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--in` | Yes | - | Input file or directory |
| `--writing-mode` | Yes | - | `vertical` or `horizontal` |
| `--model` | Yes | - | `flash`, `thinking`, or `pro` |
| `--out` | No | auto | Output file or directory |
| `--page-separator` | No | `---` | Separator text between pages |
| `--no-save-raw` | No | raw enabled | Disable raw OCR output |

## Supported inputs

- `.jpg`, `.jpeg`, `.png`, `.webp`, `.pdf`

Directory input mode:

- Non-recursive (direct children only)
- Unsupported files are ignored

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

Directory hints for `--out`:

- Path ends with `/` or `\`
- Path already exists as a directory
- Path has no suffix

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Gemini API key |
| `PDF2MD_MODEL_FLASH` | No | `gemini-2.5-flash` | Model ID for `flash` |
| `PDF2MD_MODEL_THINKING` | No | `gemini-2.5-flash` | Model ID for `thinking` |
| `PDF2MD_MODEL_PRO` | No | `gemini-2.5-pro` | Model ID for `pro` |

## Fidelity policy

- Preserve line breaks and punctuation
- Preserve paragraph order
- Do not infer missing words
- Use explicit unreadable marker when needed
- Keep multi-page separation with configured separator

# nano-banana Skill Reference (Codex)

## Runtime

- Script: `scripts/generate_image.py`
- API endpoint base: `https://generativelanguage.googleapis.com/v1beta/models`
- Default model: なし（`--model` または `--model-preset` を必須指定）

## CLI

```bash
python3 scripts/generate_image.py <prompt> [output] [--size SIZE] [--model MODEL] [--model-preset PRESET]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `prompt` | Yes | - | Text prompt for image generation |
| `output` | No | auto path in `/mnt/e/Documents/Pictures/画像生成` | File path or directory path |
| `--size` | No | `1K` | Image size: `512`, `1K`, `2K` |
| `--model`, `-m` | One of model options is required | - | Gemini model ID (`--model-preset` と排他) |
| `--model-preset` | One of model options is required | - | Preset alias: `flash31` or `pro3` (`--model` と排他) |

## Model selection priority

1. `--model`
2. `--model-preset`

## Model presets

- `flash31` -> `gemini-3.1-flash-image-preview`
- `pro3` -> `gemini-3-pro-image-preview`

## Output resolution rules

- `output` omitted -> `/mnt/e/Documents/Pictures/画像生成/YYYYMMDD_HHMMSS__<slug>.png`
- `output` is a file path -> save exactly there
- `output` is a directory path -> auto filename in that directory

Directory path is recognized when one of these is true:

- path ends with `/` or `\`
- path already exists as a directory
- path has no file extension

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Gemini API key |
| `IMAGE_SIZE` | No | `1K` | Default size if `--size` is omitted |

## Examples

```bash
# Default output directory + auto filename
python3 scripts/generate_image.py --model-preset flash31 "A serene mountain landscape at dawn"

# Explicit file path
python3 scripts/generate_image.py --model-preset pro3 "Minimalist logo" "./assets/logo.png"

# Directory path + auto filename
python3 scripts/generate_image.py --model-preset flash31 "Landing page hero" "./assets/heroes"

# High resolution
python3 scripts/generate_image.py --size 2K --model-preset flash31 "Detailed portrait"
```

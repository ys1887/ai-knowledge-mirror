# nano-banana (Codex)

Codex ワークフローで Google Gemini による画像生成を行うスキルです。

## このスキルでできること

- Gemini で画像を生成し、PNG として保存する。
- 実行スクリプト `scripts/generate_image.py` を利用する。
- 単体スクリプト実行と、Codex の複合タスク内での利用の両方に対応する。

## 前提条件

- Python 3.6 以上
- スクリプト実行シェルに `GEMINI_API_KEY` が設定されていること

例（WSL/macOS/Linux）:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## デフォルト出力の挙動

- 既定ディレクトリ: `/mnt/e/Documents/Pictures/画像生成`
- 既定ファイル名形式: `YYYYMMDD_HHMMSS__<slug>.png`

出力ルール:

- `output` を省略した場合: 既定ディレクトリに自動ファイル名で保存。
- `output` がファイルパスの場合: 指定したファイルパスに保存。
- `output` がディレクトリパスの場合: そのディレクトリに自動ファイル名で保存。

## スクリプトの使い方

```bash
python3 scripts/generate_image.py --model-preset flash31 "A sunset over mountains"
python3 scripts/generate_image.py --model-preset pro3 "An app icon" "/mnt/e/Documents/Pictures/画像生成/custom.png"
python3 scripts/generate_image.py --model-preset flash31 "Hero visual" "/mnt/e/Documents/Workspace/images/landing"
python3 scripts/generate_image.py --size 2K --model-preset flash31 "High-res landscape"
python3 scripts/generate_image.py --model-preset pro3 "A logo"
python3 scripts/generate_image.py --model gemini-3-pro-image-preview "A logo"
```

## パラメータ

- 位置引数 `prompt`（必須）
- 位置引数 `output`（任意）: ファイルまたはディレクトリのパス
- `--size`: `512` / `1K` / `2K`
- `--model` または `-m`: Gemini モデル ID（`--model-preset` と排他）
- `--model-preset`: `flash31` / `pro3`（`--model` と排他）
- モデルは `--model` または `--model-preset` のどちらか一方が必須

モデル選択の優先順位:
1. `--model`
2. `--model-preset`

## 環境変数

- `GEMINI_API_KEY`（必須）
- `IMAGE_SIZE`（任意、既定値 `1K`）

## ファイル構成

```text
nano-banana/
├── SKILL.md
├── README.md
├── reference.md
├── examples.md
└── scripts/
    └── generate_image.py
```

# pdf2md-gemini (Codex)

Gemini API を利用して、日本語文書を原文忠実に OCR し、Markdown に保存するスキルです。
API 経由で、入力から Markdown 保存まで全自動で処理します。

## このスキルでできること

- PDF/画像入力を Gemini API で処理し、`.md` まで自動生成する。
- 入力ファイル/入力フォルダを OCR して `.md` を生成する。
- 縦書き/横書きを明示指定して誤認識を減らす。
- モデルを `flash` / `thinking` / `pro` から選択する。
- PDF入力時は図表画像を抽出し、Markdownへ画像リンクを埋め込む（既定有効）。
- OCR 生テキスト（raw）を既定で保存し、監査と再確認をしやすくする。

## 前提条件

- Python 3.8 以上
- `GEMINI_API_KEY` が設定済み

例:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

## 基本仕様

- 日本語専用（言語指定なし）
- 原文忠実（改行・句読点・段落順を維持）
- ページ区切りは `---`（多ページ時）
- サブフォルダは処理しない（入力直下のみ）
- 対応入力: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.webp`

## 使い方

```bash
python3 scripts/pdf_to_md.py \
  --in "/mnt/e/Documents/Workspace/inbox/kokoro-pages" \
  --writing-mode vertical \
  --model pro
```

### 必須オプション

- `--in`: 入力ファイルまたは入力フォルダ
- `--writing-mode`: `vertical` または `horizontal`
- `--model`: `flash` / `thinking` / `pro`

### 任意オプション

- `--out`: 出力先（未指定なら既定ルール）
  - ファイル指定: 単一入力時のみ有効
  - ディレクトリ指定: `md/` と `raw/` を配下に作成
- `--page-separator`: 既定 `---`
- `--no-save-raw`: raw 出力を無効化
- `--no-extract-images`: PDF画像抽出を無効化
- `--no-embed-images`: 画像抽出は行うがMarkdown埋め込みを無効化
- `--images-dir`: 画像出力先ルートを明示指定
- `--image-format`: 画像形式（現状 `png` のみ）

## 出力ルール

既定出力ベース:

`/mnt/e/Documents/Workspace/ocr`

出力構造:

```text
ocr/<自動決定フォルダ名>/
├── images/
│   └── <input_stem>/
│       └── pNNN_imgNNN.png
├── md/
│   └── <input_stem>.md
└── raw/
    └── <input_stem>.raw.txt
```

`--out` の解決:

- 未指定: 上記の既定構造を使用
- ディレクトリ指定: `<out>/md` と `<out>/raw` を使用
- ファイル指定: 単一入力時のみ、そのファイルへ `.md` を保存
  - raw は `<そのファイルの親>/raw/<stem>.raw.txt`
- 画像は既定で `<out>/images/<stem>/`（または既定出力配下）に保存

## タイトル（出力フォルダ名）自動化

- 入力がフォルダ: フォルダ名を使用
- 入力がファイル: 拡張子なしファイル名を使用
- 禁止文字 `\\ / : * ? " < > |` は `_` に置換
- 置換後に空になる場合は `untitled`
- 同名が既に存在する場合は末尾にタイムスタンプを付与

## モデルマッピング

`--model` は内部で Gemini モデル ID に変換します。

- `flash` -> `PDF2MD_MODEL_FLASH`（既定: `gemini-2.5-flash`）
- `thinking` -> `PDF2MD_MODEL_THINKING`（既定: `gemini-2.5-flash`）
- `pro` -> `PDF2MD_MODEL_PRO`（既定: `gemini-2.5-pro`）

必要に応じて環境変数で上書きしてください。

## よくある失敗

- `GEMINI_API_KEY` 未設定
- `--out` をファイル指定したのに `--in` がフォルダ
- 入力フォルダに対応拡張子が存在しない

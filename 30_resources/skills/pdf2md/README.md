# pdf2md (Codex)

ローカルツールだけで、PDFから文章を抽出してMarkdownに保存するスキルです。
APIキーは不要です。

## このスキルでできること

- PDFを入力して `.md` を生成する（単一ファイル/フォルダ入力）。
- テキストPDFは `pdftotext` で抽出する。
- 抽出文字数が少ない場合は `ocrmypdf` で自動OCRして再抽出する。
- PDF内の図表画像を抽出し、Markdownへ画像リンクを埋め込む（既定有効）。
- 抽出生テキスト（raw）を既定で保存する。

## 対応入力

- `.pdf` のみ
- フォルダ入力は直下のみ処理（サブフォルダは処理しない）

## 事前準備（このPCで1回）

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils ocrmypdf tesseract-ocr tesseract-ocr-jpn qpdf
```

`qpdf` は将来の拡張向けですが、同時に入れておく前提にしています。

## 使い方

```bash
python3 scripts/pdf_to_md.py \
  --in "/mnt/e/Documents/Workspace/inbox/sample.pdf"
```

### 主なオプション

- `--in`: 入力PDFまたは入力フォルダ（必須）
- `--out`: 出力先（未指定なら既定ルール）
- `--lang`: OCR言語（既定: `jpn`）
- `--min-chars`: OCRへ切り替える判定閾値（既定: `40`）
- `--page-separator`: ページ区切り（既定: `---`）
- `--no-save-raw`: raw保存を無効化
- `--no-extract-images`: 図表画像抽出を無効化
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

- 未指定: 上記の既定構造
- ディレクトリ指定: `<out>/md` と `<out>/raw`
- ファイル指定: 単一入力時のみ、そのファイルへ `.md` 保存
  - raw は `<そのファイルの親>/raw/<stem>.raw.txt`
- 画像は既定で `<out>/images/<stem>/`（または既定出力配下）に保存

## 処理フロー（自動）

1. `pdftotext` で抽出
2. 抽出文字数が `--min-chars` 未満なら `ocrmypdf` でOCR
3. OCR後PDFを再度 `pdftotext` で抽出
4. 図表画像を抽出し（既定有効）、Markdownへリンク挿入
5. Markdown/Rawを保存

## よくある失敗

- `pdftotext` または `ocrmypdf` が未導入
- `--out` をファイル指定したのに `--in` がフォルダ
- 入力フォルダにPDFが存在しない

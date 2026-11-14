# PDF2MD-GEMINI Request

## 必須
- Input path: <対象フォルダ or 対象ファイル>
- Writing mode: <vertical | horizontal>
- Model: <flash | thinking | pro>

## 任意
- Output path: <未指定 | 出力フォルダ | 出力mdファイル>
- Notes: <補足（薄い文字、傾き、ルビ、ノイズ等）>

## skill既定動作（入力不要）
- 日本語専用（ja固定）
- 原文忠実（strict）
- raw OCRは既定で保存
- ページ区切りは `---`
- サブフォルダは処理しない（入力直下のみ）
- 既定出力:
  - /mnt/e/Documents/Workspace/ocr/<自動決定フォルダ名>/md/*.md
  - /mnt/e/Documents/Workspace/ocr/<自動決定フォルダ名>/raw/*.raw.txt

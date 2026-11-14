# PDF2MD Request

## 必須
- Input path: <対象PDF or 対象フォルダ>

## 任意
- Output path: <未指定 | 出力フォルダ | 出力mdファイル>
- OCR language: <既定 jpn>
- OCR threshold: <既定 40>
- Notes: <補足>

## skill既定動作（入力不要）
- PDFのみ対象
- 先に `pdftotext` で抽出
- 抽出量が不足したら `ocrmypdf` で自動OCR
- raw抽出テキストは既定で保存
- ページ区切りは `---`
- サブフォルダは処理しない（入力直下のみ）
- 既定出力:
  - /mnt/e/Documents/Workspace/ocr/<自動決定フォルダ名>/md/*.md
  - /mnt/e/Documents/Workspace/ocr/<自動決定フォルダ名>/raw/*.raw.txt

---
name: nano-banana
description: Geminiのnanobananaを使用するskill。
---

# nano-banana (Codex)

## 目的
Google Gemini の画像生成APIで画像を生成し、PNGとして保存する。

## 前提
- WSL（Ubuntu）+ bash
- Python（通常 `python3` で実行）
- 環境変数 `GEMINI_API_KEY` が **Ubuntu側**で設定済みであること

## 実体（スクリプト）
- `scripts/generate_image.py`

## 実行時ルール（Codex対話）
- `$nano-banana` 呼び出し時、ユーザーの最初の指示文にモデル指定（flash31 / pro3）があればそれに従う。
- 最初の指示文にモデル指定がない場合は、生成前に `flash31` または `pro3` の選択を必ず確認する。
- モデルが確定するまでは画像生成を実行しない。

## 出力
- 出力フォルダ（固定）  
  `/mnt/e/Documents/Pictures/画像生成`
- 既定の命名規則（output省略時）  
  `YYYYMMDD_HHMMSS__<slug>.png`  
  `<slug>` はプロンプト由来の短い文字列（Windowsで安全な文字に整形）
  - Windows禁止文字 `\ / : * ? " < > |` は `_` に置換
  - その他の記号は除去される

## 使い方
### 1) 出力先を省略して生成（推奨）
- `output`（第2引数）を省略すると、自動命名で固定フォルダへ保存する。
- 出力先フォルダが存在しない場合は自動作成される。

入力：
- 第1引数：プロンプト（必須）

結果：
- `/mnt/e/Documents/Pictures/画像生成` に PNG が生成される。

例：
- `python3 scripts/generate_image.py --model-preset flash31 "A sunset over mountains"`

### 2) 出力パスを指定して生成（任意）
- `output`（第2引数）を指定すると、その指定を優先する。
- `output` が**ファイルパス**の場合は、そのファイル名で保存。
- `output` が**フォルダパス**の場合は、そのフォルダ配下に自動命名で保存。
- フォルダ扱いの条件: 末尾が `/` または `\`、既存ディレクトリ、拡張子なしパス。
- 拡張子は `.png` 推奨（明示ファイル指定時。スクリプトは拡張子の検証を行わない）。

例：
- `python3 scripts/generate_image.py --model-preset pro3 "An app icon" /mnt/e/Documents/Pictures/画像生成/custom.png`
- `python3 scripts/generate_image.py --model-preset flash31 "A hero visual" /mnt/e/Documents/Workspace/images/landing`

## パラメータ
- `--size`：`512` / `1K` / `2K`（環境変数 `IMAGE_SIZE` より優先）
- `--model`：モデルID（`--model-preset` と排他、最優先）
- `--model-preset`：`flash31` / `pro3`（`--model` と排他）
- モデル指定は `--model` または `--model-preset` のどちらか一方が必須

モデル選択の優先順位:
1. `--model`
2. `--model-preset`

プリセット対応:
- `flash31` -> `gemini-3.1-flash-image-preview`
- `pro3` -> `gemini-3-pro-image-preview`

## 動作確認
- `画像生成` フォルダに PNG が作成されていること
- ファイル名が `YYYYMMDD_HHMMSS__<slug>.png` になっていること（output省略時）

## よくある失敗
- `GEMINI_API_KEY is not set`  
  → Ubuntu側で `GEMINI_API_KEY` が未設定／シェルに反映されていない
- 生成は成功するが保存できない  
  → 出力先パスの誤り、または権限の問題

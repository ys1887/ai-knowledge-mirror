# EPUB Splitter (v2)

Split a combined EPUB into per-volume EPUBs using spine cover markers.
This is a v2 workflow that favors reliability over optimization.

## 概要
- EPUB を分割して巻ごとの EPUB を生成するツール

## 使い方
- 例: `python split_epub.py input.epub`

## 入力/出力
- 入力: 1つの EPUB ファイル
- 出力: 分割後の EPUB を `output/` に保存
- ログ/一時ファイル: `split_log.txt` にログ出力、作業用ファイルは `output/` 配下で作成

## 注意点
- 元 EPUB のバックアップ推奨
- 分割マーカーは `*-p-cover` を想定（例: `vol1-p-cover`）

## Requirements
- Python 3.9+
- lxml

Install dependencies:





<!-- PR test -->


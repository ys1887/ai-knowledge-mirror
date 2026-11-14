# comparisons

`docs/comparisons/` は、3系統比較の一次記録を置く場所です。

## 基本ルール

- 1質問につき 1 Markdown
- 回答本文はそのまま残す
- 比較メモでは、回答の中身と運用メトリクスを分けて書く

## 最低限のメモ項目

- `selected_file_count`
- `selected_files`
- `実行時間`
- `validator`
- `構造`
- `解釈の芯`
- `判定`

## このブランチでの見方

- `iching-sdk` は `codex/split-extract-sources-by-hexagram` を基準にする
- `EX_SIMPLE` では `selected_file_count = 2` を期待値とする
- 過去記録が旧 source 契約で取られている場合は、その旨をメモに残し、必要なら再測定欄を分ける

## 2026-03-11 の進行判断

- citation path 修正後の `EX_SIMPLE` 2 件再実測では、どちらも `selected_file_count = 2`、期待ファイル一致、validator pass を確認
- 参照行も `honda_wataru/34_雷天大壮.md` のようなサブディレクトリ付き実ファイル名で通るようになった
- source selection と validator 契約の両方が揃ったので、比較運用は次の `EX_5` に進めてよい

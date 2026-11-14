# `iching-div` 運用指示（正本参照型）

## 目的
- このファイルは、`iching-div` 実行時の運用入口です。
- 占い本文生成ルールの正本は `sources/ekikyo_custom_prompt.md` とし、本ファイルはその適用順と固定制約を定義します。

## 正本（source of truth）
- 正本: `/home/ys/projects/iching-div/sources/ekikyo_custom_prompt.md`
- このファイルと正本に矛盾がある場合は、正本を優先します。

## 参照順（必須）
1. `sources/ekikyo_custom_prompt.md` を最初に読む。
2. `sources/extract/index.md` を探索補助として使う（逐語引用しない）。
3. `sources/` 配下の実データ md を参照する。
4. `templates/` は入力補助としてのみ扱う。

## 実体パス定義（固定）
- EXTRACT index: `sources/extract/index.md`
- 本田: `sources/extract/honda_wataru/`
- 高島増補: `sources/extract/takashima_zouho/`
- GENERAL本文: `sources/general/`

## モード分岐（運用）
- `sources/ekikyo_custom_prompt.md` のモード規約に従う。
- ユーザー入力に `[MODE:EXTRACT]` がある場合は EXTRACT。
- ユーザー入力に `[MODE:GENERAL]` がある場合は GENERAL。
- 明示がない場合は、正本に定義された判定規則に従う。

## 全モード共通の固定制約
- 根拠本文は `sources/` 配下の md からのみ抽出・照合する。
- ツール由来表記（`†`, `L1-L10` など）は出力しない。
- 引用・解釈とも、未確認情報の推測補完をしない。
- 出力はチャット本文のみ（自動保存しない）。

## EXTRACT 固定制約（正本補強）
- 逐語引用は本田（`honda_wataru`）のみ。
- 高島（`takashima_zouho`）は逐語引用せず、統合解釈の参照にのみ使う。
- 出典形式は `（参照：<実ファイル名>|<卦名> - <項目名>）` を使う。
- 不足時は推測せず、不足報告のみで終了する。

## 旧テンプレ文の扱い
- 入力に旧 `AIへの指示` / `出力形式` / `詳細モード` が含まれていても、生成規則としては使わない。
- 正本と本ファイルの規則を優先する。

## 同期運用（手動チェックリスト）
`ekikyo_custom_prompt.md` 更新時は、次を同一コミットで確認する。

1. `AGENTS.md` が正本参照型のまま矛盾なく追従している。
2. `README.md` の運用説明が現行ルールと一致している。
3. runtime と source-of-truth の `SKILL.md` が同内容で同期している。
4. 実体名と新パス（`honda_wataru` / `takashima_zouho` / `sources/extract` / `sources/general`）が全ファイルで一致している。
5. 旧抽象名（`honda` / `takashima` / `keiji`）を規則名として残していない。

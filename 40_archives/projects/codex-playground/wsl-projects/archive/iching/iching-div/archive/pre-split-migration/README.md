# 易経占いプロジェクト（`iching-div`）

このリポジトリは、易経の入力（本卦・変爻など）に基づき、ローカル `sources/` から本文を抽出・照合して回答するための運用プロジェクトです。

## ルールの優先順位

1. 正本: `sources/ekikyo_custom_prompt.md`
2. 実行入口: `AGENTS.md`
3. 入力補助: `templates/`

- `AGENTS.md` は正本の参照・適用ルールを定義する運用入口です。
- ルールの矛盾時は常に `ekikyo_custom_prompt.md` を優先します。

## ディレクトリ構成

```text
iching-div/
├─ AGENTS.md                     # 運用入口（正本参照型）
├─ README.md
├─ sources/
│  ├─ ekikyo_custom_prompt.md    # ルール正本
│  ├─ extract/
│  │  ├─ index.md                # EXTRACT用の検索補助インデックス
│  │  ├─ honda_wataru/           # 本田 64卦
│  │  └─ takashima_zouho/        # 高島増補 64卦
│  └─ general/
│     ├─ keiji_jouden_1-12.md
│     ├─ keiji_kaden_1-12.md
│     ├─ honda_wataru_eki_sanden.md
│     ├─ honda_wataru_eki_jobun.md
│     └─ 他、GENERAL参照用md
├─ templates/                    # 入力テンプレート（参照用）
├─ work/                         # 作業メモ（git管理外）
└─ skills/                       # 将来用
```

## モード運用

- `EXTRACT`: 卦・爻入力をもとに本文抽出と解釈を行う。
- `GENERAL`: 易に関する一般質問・比較に回答する。
- 詳細な分岐と制約は `sources/ekikyo_custom_prompt.md` に従います。

## 主要制約（要点）

- 根拠本文は `sources/` 配下の md のみを参照。
- EXTRACT の探索起点は `sources/extract/index.md`。
- EXTRACT の逐語引用は `sources/extract/honda_wataru/` のみ。
- `sources/extract/takashima_zouho/` は統合解釈の参照用途（逐語引用しない）。
- GENERAL は `sources/general/` 配下の md を参照する。
- 出典形式は `（参照：...）`。
- 推測補完は禁止。不足時は不足報告で終了。

## 使い方

1. Codex で `$iching-divination` を入力。
2. 質問文全文を貼る（テンプレ完全一致は不要）。
3. チャット本文として出力を受け取る（自動保存なし）。

## テンプレートについて

- `templates/` は入力補助です。
- 入力内に旧 `AIへの指示` や `出力形式` が含まれていても、生成規則としては使いません。
- 生成規則は常に正本 + `AGENTS.md` を優先します。

## 更新運用（手動同期）

`ekikyo_custom_prompt.md` 更新時は次を確認してください。

1. `AGENTS.md` の運用入口記述が正本と矛盾しない。
2. `README.md` の優先順位・モード説明が一致している。
3. 以下2ファイルの `SKILL.md` が同期されている。
   - `/mnt/c/Users/nekol/.codex/skills/iching-divination/SKILL.md`
   - `/home/ys/projects/lib-skills/codex/iching-divination/SKILL.md`
4. 実体名と新パス（`honda_wataru` / `takashima_zouho` / `sources/extract` / `sources/general`）が統一されている。

## Git 管理方針

- `sources/` と `work/` は `.gitignore` で管理対象外です。
- このため、正本更新はローカル運用で行い、必要に応じて手動同期します。

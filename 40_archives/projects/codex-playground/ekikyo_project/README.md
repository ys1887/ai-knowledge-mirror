# ekikyo

易経関連の `sources/`, `prompts/`, `scripts/` をまとめて管理する統合リポジトリです。

## Purpose

- `sources/`, `prompts/`, `scripts/` を 1 つのリポジトリ内で階層表示する
- GitHub 上で構成・差分・履歴を見やすくする

## Operating Rule (Important)

- 日常の編集・commit・push はこのリポジトリ（`ekikyo`）で行う
- `sources/`, `prompts/`, `scripts/` をこのリポジトリの正本として扱う
- 保存先/基準（GitHub正本）は `origin/main`（`ys1887/ekikyo`）
- ローカル `ekikyo` は日常編集を行う作業コピーとして扱う
- 旧個別リポジトリは GitHub から削除済み（ローカルに旧 `.git` が残っているものは後で整理）

## Daily Workflow (GitHub Source of Truth)

1. ローカル `ekikyo` で編集
2. 変更確認
   - `git status -sb`
   - `git diff --stat`
3. 問題なければ commit
4. `git push` で `origin/main` に保存

### Important Notes

- 未commit/未push の変更は GitHub には存在しない（PC故障時に復元不可）
- ローカルでファイルを削除しても、`commit + push` しない限り GitHub には反映されない
- 大きな削除を行う前は、必要に応じてバックアップ用ブランチを切る
  - 例: `git branch backup-YYYYMMDD`
- `git pull` は `--ff-only` を推奨
  - 例: `git pull --ff-only`

## Current Layout

### sources

- `sources/eki_book`
- `sources/honda_wataru_64`
- `sources/takashima_zouho_64`
- `sources/ekikyo_juuyoku_keiji`
- `sources/ekikyo_project_source`
- `sources/chienomori`
- `sources/takashima_kantogen`

### prompts

- `prompts/ekikyo_custom_prompt.md`

### scripts

- `scripts/iching-div`
- `scripts/update_obsidian_related_ideas.py`

## Notes

- `project_source/index.md` を参照起点として運用する（EXTRACT/GENERAL の参照整理に対応）
- 一部 `sources/*` に旧個別repo由来の `.git` が残っているため、必要に応じて整理する
- subtree 統合時の補助 remote は削除済み。通常運用では `origin` のみ使用
- `iching-hexagram-utils` と `i-ching-calculator` は `apps` リポジトリへ移動済み

## プロンプト更新印の自動化

`prompts/ekikyo_custom_prompt.md` の1行目は、コミット時に `YYYY-MM-DD.n` 形式へ自動更新します。

### 初期設定（1回のみ）

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit scripts/update_prompt_version_stamp.sh
```

### 更新印ルール

- 対象: `project_source/prompts/ekikyo_custom_prompt.md` がステージされているコミットのみ
- 当日と同じ日付:
  - `YYYY-MM-DD.n` -> `n+1`
  - `YYYY-MM-DD` -> `.2`
- 日付が変わったら `YYYY-MM-DD.1` にリセット

### 動作例

- 1回目: `運用版 2026-03-02.1`
- 2回目: `運用版 2026-03-02.2`
- 3回目: `運用版 2026-03-02.3`

### 一時的な回避

緊急時のみ `git commit --no-verify` でフックをスキップできます。

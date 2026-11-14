# custom_prompts

ChatGPT custom prompts 関連ファイルをまとめて管理するリポジトリです。

## Purpose

- `chatgpt_personalize/` を 1 つのリポジトリ内で履歴管理する
- GitHub 上で構成・差分・履歴を見やすくする

## Operating Rule (Important)

- 日常の編集・commit・push はこのリポジトリ（`custom_prompts`）で行う
- `chatgpt_personalize/` をこのリポジトリの正本として扱う
- 保存先/基準（GitHub正本）は `origin/main`（`ys1887/custom_prompts`）
- ローカル `custom_prompts` は日常編集を行う作業コピーとして扱う

## Daily Workflow (GitHub Source of Truth)

1. ローカル `custom_prompts` で編集
2. 変更確認
   - `git status -sb`
   - `git diff --stat`
3. 問題なければ commit
4. `git push` で `origin/main` に保存

### Important Notes

- 未commit/未push の変更は GitHub には存在しない
- ローカルでファイルを削除しても、`commit + push` しない限り GitHub には反映されない
- `git pull` は `--ff-only` を推奨
  - 例: `git pull --ff-only`

## Current Layout

- `chatgpt_personalize/`
- `chatgpt_personalize/あなたについての詳細.md`
- `chatgpt_personalize/カスタム指示.md`

## Initial Checks After Clone

- `git remote -v`
- `git branch --show-current`
- `git status -sb`

## Prompt Header Stamp Automation

`chatgpt_personalize/あなたについての詳細.md` と `chatgpt_personalize/カスタム指示.md` の1行目は、コミット時に `# ファイル名 YYYY-MM-DD.n` 形式へ自動更新します。

### Initial Setup

```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit scripts/update_prompt_header_stamp.sh
```

### Stamp Rules

- 対象: 上記2ファイルがステージされているコミットのみ
- タイトル: ファイル名そのままを使う
- 当日の初回更新: `YYYY-MM-DD.1`
- 同日の2回目以降: `YYYY-MM-DD.2`, `YYYY-MM-DD.3` と増える
- 日付が変わったら `YYYY-MM-DD.1` に戻る

### Notes

- 1行目は運用用の更新印として扱う
- AI に渡す本文では、必要に応じて1行目を除外して使う
- 緊急時のみ `git commit --no-verify` で hook をスキップできる

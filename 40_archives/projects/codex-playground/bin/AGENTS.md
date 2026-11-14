# Bin AGENTS

## Scope
- This file defines `E:\Documents\Playground\bin`-specific overrides.
- Global defaults from `C:\Users\nekol\.codex\AGENTS.md` still apply unless overridden here.

## README language policy
- README は日本語で作成・更新すること。
- AI で README を生成・更新する場合も、日本語を優先すること。
- コマンド、パス、ファイル名などの英数字はそのまま保持すること。

## GitHub Visibility Policy
- GitHub repository visibility defaults to Private in this workspace.
- When using `gh repo create`, always set visibility explicitly and use `--private` unless this repo's policy says otherwise.
- `--public` or `--internal` is permitted only when this project's `AGENTS.md` explicitly declares the exception.

## Script Operations Policy
- Prefer small, composable scripts with clear inputs/outputs.
- For scheduler-related scripts, validate dry-run or non-destructive behavior first when possible.
- Avoid destructive commands unless explicitly requested.
- Report exact verification commands used after script changes.

## Git Publish Policy (Semi-Auto)
- In this repo, when the user asks to "commit" (or equivalent), use `safe-git-publish` and prepare push as the default next step.
- Do not push silently: always ask one short final confirmation immediately before push.
- If the user explicitly asks to push, treat it as push permission.
- Keep `main`/`master` guardrails enabled; only allow intentional main/master push.

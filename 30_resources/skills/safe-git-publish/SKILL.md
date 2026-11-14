---
name: safe-git-publish
description: Gitの変更を安全にコミットしてプッシュするskill。
---

# Safe Git Publish (Codex)

## Purpose
Provide a safe, repeatable workflow for staging, committing, and optionally pushing git changes.

## Why this exists
- Reduces manual mistakes in routine git publishing.
- Adds guardrails before commit/push (secrets, branch safety, clean intent).
- Keeps Codex behavior aligned with explicit user intent for push actions.

## Safety Rules
- Never push silently.
- Default policy: push only when the user explicitly asks to push.
- Semi-auto policy (repo opt-in): for `commit`-intent requests, stage+commit first, then ask one short confirmation before push.
- Default to private-safe behavior (`main`/`master` push is blocked unless explicitly allowed).
- Block staged `.env` and common secret-like patterns.
- Prefer small, intentional commits over broad `git add .`.

## Natural Language Triggers
- If the user says `pushして` or `git管理して`, treat it as explicit permission to commit and push.
- If the user says `commitして` (or equivalent), treat it as commit intent. In repos that opt in to semi-auto, proceed to one push confirmation after commit.
- For explicit push requests targeting `main`/`master`, include `--allow-main-push`.
- Default execution for this workflow is:
  - `--stage-all --push --allow-main-push --auto-sync-on-push --retry-push-on-reject`

## Files
- Script: `scripts/safe_git_publish`

## Usage
From this skill folder:

```powershell
py .\scripts\safe_git_publish --message "docs: update skill notes"
```

Commit with auto-generated message:

```powershell
py .\scripts\safe_git_publish --stage-all --auto-message ai-summary
```

Commit and push current branch:

```powershell
py .\scripts\safe_git_publish --message "feat: add safe git publish skill" --push --auto-sync-on-push
```

Stage specific files, then commit:

```powershell
py .\scripts\safe_git_publish --path README.md --path safe-git-publish\SKILL.md --message "docs: add git publish skill docs"
```

Preview commands only:

```powershell
py .\scripts\safe_git_publish --stage-all --auto-message timestamp --push --allow-main-push --auto-sync-on-push --dry-run
```

Push to `main` intentionally:

```powershell
py .\scripts\safe_git_publish --message "chore: release notes" --push --allow-main-push
```

## Options
- `--message <text>`: commit message.
- `--auto-message <mode>`: auto-generate message (`ai-summary`, `timestamp`).
- `--path <path>`: stage one path (repeatable).
- `--stage-all`: stage all tracked/untracked changes.
- `--push`: push after a successful commit.
- `--allow-main-push`: allow push on `main`/`master`.
- `--auto-sync-on-push`: on push reject, run `fetch + rebase` then retry once.
- `--retry-push-on-reject`: keep retry behavior enabled (default).
- `--no-retry-push-on-reject`: disable retry behavior.
- `--dry-run`: print planned commands without changing git state.
- `--help`: show help.

## Notes
- If `--path` and `--stage-all` are both omitted, the script commits already staged changes only.
- Use either `--message` or `--auto-message`.
- If secret checks fail, fix or unstage before retrying.
- The helper is Windows-native Python and should be run with `py` in Codex desktop sessions.

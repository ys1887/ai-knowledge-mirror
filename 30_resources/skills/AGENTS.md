# Repo AGENTS (`E:\Documents\Playground\lib-skills`)

## Scope
- This file defines repository-local overrides for git publish behavior.
- Global defaults from `C:\Users\nekol\.codex\AGENTS.md` still apply unless overridden here.

## GitHub Visibility Policy
- GitHub repository visibility defaults to Private in this repository.
- When using `gh repo create`, always set visibility explicitly and use `--private` unless this repo's policy says otherwise.
- `--public` or `--internal` is permitted only when this repository's `AGENTS.md` explicitly declares the exception.

## Repo Source-of-Truth Policy
- For this repository, GitHub `origin/main` (`ys1887/lib-skills`) is the source of truth for recovery.
- Local repository at `E:\Documents\Playground\lib-skills` is the working copy for day-to-day edits.
- Treat task completion as including commit + push to `origin/main`, unless explicitly instructed otherwise.

## Branch Communication Policy
- Branch-based work is allowed when needed, but must be explicitly announced before starting work.
- When using a branch, report the branch name and state that final reflection to `main` is required for completion.
- Branch push alone is not considered completion; completion requires integration to `main` and push to `origin/main`.
- End-of-task report must include:
  - working branch used
  - whether `main` reflection is done
  - ahead/behind status for `main` vs `origin/main`
  - push-target (`origin/main` or `origin/<branch>`)
  - origin-url (current `origin` remote URL)
  - main-reflected (`done` or `not done`)
- `main-reflected: done` means the work is integrated into `main` and pushed to `origin/main`.
- `main-reflected: not done` means changes exist only on a branch and are not yet reflected to `main`.
- `git check` examples:
  - main case: `push-target: origin/main`, `main-reflected: done`
  - branch case: `push-target: origin/<branch>`, `main-reflected: not done`

## Git Publish Policy (Auto)
- In this repo, treat completion of requested implementation tasks as permission to run commit and push without an extra confirmation step.
- Use `safe-git-publish` with push enabled by default for repo changes.
- Allow direct push to `main`/`master` in this repo when publishing task changes.
- On push rejection, prefer existing `safe-git-publish` auto-sync behavior (`fetch + rebase` then one retry).

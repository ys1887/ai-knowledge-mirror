# Codex Runtime Rules

This reference captures the local operating assumptions for custom Codex skills in this workspace.

## Source Of Truth And Runtime

- Edit custom skill sources in `E:\Documents\Playground\lib-skills`.
- WSL and Windows `.codex` homes are intentionally operated separately.
- Treat `C:\Users\nekol\.codex\skills` and, when still needed, `/home/ys/.codex/skills` as runtime deployment targets only.
- Do not assume a runtime copy is the authoring source-of-truth, even if the current session loads from it.
- Before saying a skill is "installed", verify that the required runtime copy or copies were actually updated.

## Deployment Boundary

- `skill-installer` is for fetching skills from curated sources or GitHub.
- Locally authored skills should be edited and validated in this repo first.
- Runtime sync is a separate step from authoring.
- In this workspace, the default runtime sync target is `C:\Users\nekol\.codex\skills`.
- If runtime sync is requested, verify the Windows runtime destination unless the user explicitly narrows or expands the target. Verify `/home/ys/.codex/skills` only when WSL runtime support is still needed or explicitly requested.

## Repo Workflow Expectations

- Read the applicable `AGENTS.md` and `codex-rules.yaml` before major edits.
- For new skills or multi-file logic changes, prefer a working branch.
- Keep changes minimal, clear, and reversible.
- Use self-review before completion and report remaining risks or unverified items.

## Reporting Expectations

For substantial tasks, report:

- what changed
- how it was verified
- remaining risks or assumptions
- `ai-notes update: done|not done`
- the required git check block

## Agent Metadata Reminder

- `agents/openai.yaml` is UI-facing metadata.
- Keep it synchronized with the current `SKILL.md`.
- Regenerate or update it whenever trigger scope or skill framing changes.

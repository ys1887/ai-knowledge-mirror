---
name: iching-sdk
description: "易占いSDKのCLIと素材を使うskill。"
---

# iching-sdk

## Purpose
Use `/home/ys/projects/iching-sdk` as the runtime project for I Ching work.
Treat this skill as a thin wrapper around the local `iching` CLI and the files under the SDK project.

## Fixed Paths
- Project root: `/home/ys/projects/iching-sdk`
- CLI entry: `/home/ys/projects/iching-sdk/iching`
- Sources root: `/home/ys/projects/iching-sdk/sources/`
- Rules: `/home/ys/projects/iching-sdk/rules/`
- Prompts: `/home/ys/projects/iching-sdk/prompts/`
- Templates: `/home/ys/projects/iching-sdk/templates/`

## Role
- This skill is the SDK-based entrypoint for I Ching work.
- Keep `iching-divination` separate as the legacy / project-compatible path.
- Prefer `/home/ys/projects/iching-sdk` over `/home/ys/projects/iching-div` when this skill is used.

## Execution Rules
1. Read the SDK project files first when needed.
2. Prefer `./iching run` for the standard one-shot workflow. Use `iching.toml` with `default_provider = "codex"` and `[providers.codex]` for the normal path, or pass `--provider codex` explicitly when needed.
3. Use `./iching resolve` to classify the input and confirm the working mode when you need to inspect or explain the flow.
4. Use `./iching build-prompt` when you need the assembled execution prompt separately instead of a full run.
5. Use `./iching answer` when you already have a prompt and only need `prompt -> answer` execution. Prefer the provider route over presets for normal usage.
6. Use `--answer-cmd` only when you need to override the default flow for testing or custom execution. Explicit command input wins over provider and preset selection.
7. Use `./iching validate` for post-answer self-checks or citation checks when the workflow needs it.
8. Use `./iching index` as a helper when you need to inspect the registered source set for a mode.
9. Use only local Markdown files under `sources/` as evidence unless the user explicitly asks for something else.
10. Return the final answer in chat; do not save the answer to repo files unless the user asks.
11. Treat this skill as a wrapper: keep durable logic in the SDK project, not in the skill body.

## Current Commands
- `./iching index --mode extract|general`
- `./iching resolve --input <path|-> [--mode extract|general]`
- `./iching build-prompt --input <path|-> [--mode extract|general]`
- `./iching answer --prompt <path|-> [--provider codex] [--codex-model <name>] [--codex-sandbox <mode>] [--codex-approval-policy <policy>] [--answer-preset codex-exec] [--answer-cmd <cmd> [args...]]`
- `./iching run --input <path|-> [--mode extract|general] [--out-dir <dir>] [--provider codex] [--codex-model <name>] [--codex-sandbox <mode>] [--codex-approval-policy <policy>] [--answer-preset codex-exec] [--answer-cmd <cmd> [args...]]`
- `./iching validate --mode extract|general --input <path|-> [--context <resolve.json|run.json>]`

## Current Scope
- The SDK currently provides index, resolve, build-prompt, answer, run, and validation utilities.
- `answer` performs `prompt -> provider/preset/answer-cmd -> stdout` without artifact management or validation.
- `run` performs `resolve -> build-prompt -> answer -> validate` and writes artifacts under `out/run/` unless `--out-dir` is provided.
- `codex` is the current built-in provider, and `codex-exec` remains as a compatibility preset that resolves to `codex exec`.
- Answer generation normally goes through the built-in `codex` provider or an explicit `--answer-cmd`; compatibility presets remain available but are no longer the preferred path.

## Future Direction
- Keep the skill thin while moving durable workflow logic into the SDK project.
- Keep the skill wording aligned with the provider-first CLI contract while preserving preset compatibility where needed.
- Eventually support higher-level execution beyond the current preset / external-command delegation model.

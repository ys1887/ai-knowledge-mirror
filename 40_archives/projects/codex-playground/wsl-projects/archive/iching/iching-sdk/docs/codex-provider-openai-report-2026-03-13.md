# Codex Provider Runtime Report for OpenAI (2026-03-13)

## Summary

`iching-sdk` 側では provider 実行前の preflight probe、`run.json` 診断強化、failure 代表症状分類まで実装した。

そのうえで最小再試験を行った結果、`test_1.md` は preflight 段階で `readonly filesystem` を先頭症状として失敗した。
同じ stderr には `state db open failure`、`shell snapshot` failure、`stream disconnected` も含まれていた。

現時点の第一候補は `iching-sdk` ではなく、`codex exec` runtime の filesystem / state / snapshot / connection 層である。

## Fixed Premises

今回の再試験で固定できている前提は次のとおり。

- `resolved_codex_path = /home/ys/.nvm/versions/node/v22.21.1/bin/codex`
- `resolved_codex_version = codex-cli 0.114.0`
- `answer_command = codex exec --sandbox workspace-write`
- `iching-sdk` の `resolve/select/build-prompt` は正常に完了する
- provider failure 時も `run.json` へ preflight と runtime diagnostics を保存できる

## Reproduction

### 1. Direct short probe

```bash
printf 'Reply with exactly OK.\n' | /home/ys/.nvm/versions/node/v22.21.1/bin/codex exec --sandbox workspace-write -
```

Observed result:

- command itself returned `OK`
- stderr contained repeated state runtime warnings
- representative symptoms:
  - `failed to open state db`
  - `state db discrepancy`
  - `Failed to delete shell snapshot`

Interpretation:

- short probe can succeed even when runtime state handling is unhealthy
- therefore short success alone is not enough to clear runtime state/snapshot issues

### 2. Minimal SDK run

```bash
python3 ./iching run \
  --input tests/fixtures/extract_cases/test_1.md \
  --profile honda \
  --provider codex \
  --out-dir /tmp/iching-codex-min-retry-test1
```

Observed result:

- `final_status = runtime_error`
- `error_source = provider`
- `error_type = provider_sandbox_or_fs`
- `preflight_ran = true`
- `preflight_exit_code = 1`
- `error_summary = preflight failed: codex sandbox or filesystem issue (readonly filesystem) ...`

Artifacts:

- `/tmp/iching-codex-min-retry-test1/run.json`
- `/tmp/iching-codex-min-retry-test1/prompt.txt`
- `/tmp/iching-codex-min-retry-test1/resolve.json`
- `/tmp/iching-codex-min-retry-test1/select.json`

## Most Relevant stderr Symptoms

The first meaningful lines from `preflight_stderr` were:

- `WARNING: proceeding, even though we could not update PATH: Read-only file system (os error 30)`
- `failed to install system skills: ... Read-only file system`
- `failed to refresh available models: stream disconnected before completion`
- `failed to open state db at /mnt/c/Users/nekol/.codex/state_5.sqlite: ... unable to open database file`
- `failed to initialize state runtime at /mnt/c/Users/nekol/.codex`
- `Failed to create shell snapshot ... Read-only file system`
- later in the same run: repeated `stream disconnected` retries against `https://chatgpt.com/backend-api/codex/responses`

## Why `iching-sdk` Is Probably Not the Primary Cause

- `resolve/select/build-prompt` completed and wrote artifacts before provider execution
- the minimal failing case is `tests/fixtures/extract_cases/test_1.md`, not a heavy case
- `resolved_codex_path` and CLI version are stable across successful and failing investigations
- the first failure now happens in preflight, before the full prompt is sent

## Current Interpretation

Priority of likely causes:

1. `codex exec` runtime filesystem / state / snapshot constraints
2. connection / streaming instability that appears after runtime initialization trouble
3. `iching-sdk` profile or prompt preparation logic

The current evidence suggests item 3 is not the leading cause.

## Questions for OpenAI

- Is `codex exec --sandbox workspace-write` expected to require write access under `.codex` for:
  - state DB
  - shell snapshots
  - system skills installation
- Is there an official way to disable or relocate those writes fully for runtime probing?
- Is `--ephemeral` expected to bypass state DB / shell snapshot initialization in `codex-cli 0.114.0`?
- Are the repeated `stream disconnected` retries likely secondary fallout after state/snapshot initialization problems, or should they be treated as an independent transport issue?

## Requested Follow-up from Our Side

When OpenAI-side fixes or guidance arrive, we will rerun only:

1. the short probe above
2. the single minimal case `tests/fixtures/extract_cases/test_1.md`

We will not broaden to heavier cases until those two pass the preflight boundary.
